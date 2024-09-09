from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async
from django.template.loader import render_to_string
import json
from collections import defaultdict
from django.contrib.auth.models import User
from time import sleep
from .models import GroupExp, UserAnswer, TempUserAnswer
from django.shortcuts import get_object_or_404



class ControlConsumer(WebsocketConsumer):
    users = set()
    count = 0
    user_answer = defaultdict()
    fake_user_answer = defaultdict()
    MAX_TIME = 5
    time = MAX_TIME
    user_groups = defaultdict()

    time_flag = False

    def connect(self):
        self.user = self.scope['user']
        self.group= self.scope['url_route']['kwargs']['group']

         
        self.group_obj  = GroupExp.objects.get(name=self.group)
      
        

        if self.user not in self.group_obj.users.all():
            self.group_obj.users.add(self.user)
            print('users online on group: ', self.group_obj.name)
            print(self.group_obj.users.filter(is_staff=False))
    
            self.group_obj.save()


        async_to_sync(self.channel_layer.group_add)(
            self.group,
            self.channel_name
        )
        self.accept()
        self.users.add(self.user)
        group_obj = GroupExp.objects.get(name=self.group)
        self.update_online_count()
        
            
    def disconnect(self, close_code):
        self.users.discard(self.user)

        if self.user in self.group_obj.users.all():
        
            self.group_obj.users.remove(self.user)
            print(self.group_obj.users.all())
            self.group_obj.save()

        self.update_online_count()


        async_to_sync(self.channel_layer.group_discard)(
            self.group,
            self.channel_name
        )

    def receive(self, text_data):

        data = json.loads(text_data)
        print(self.count)
        print(data)
        group = ""
        event = defaultdict(str)

        if 'goto' in data:
            group = data['goto']
            print('goint to: ', group)
            event = {
                'type': 'goto_group',
                'group': group
            }
        elif 'name' in data:
            event = {
                'type': 'update_name',
                'name': data['name']
            }
        elif 'time' in data:
            print('time out')
            for user, answer in self.user_answer.items():
                user_obj = User.objects.get(username=user)
                TempUserAnswer.objects.create(user=user_obj, answer=answer, group=self.group_obj)
                UserAnswer.objects.create(user=user_obj, answer=answer, group=self.group_obj)
            print(TempUserAnswer.objects.all())
            sleep(3)
            event = {
                'type': 'next_question',
                'count': self.count + 1
            }
        elif 'control' in data:
            group = data['group']
            event = {
                'type': 'display_fake_user_answer',
                'group': group,
                'count': self.count,
                'answer': data['answer'],
                'user': data['user']
            }
        elif 'answer' in data:
            group = data['group']
            for user, answer in self.user_answer.items():
                self.user_answer[user] = answer
                print(user, answer)
            event = {
                'type': 'display_user_answer',
                'group': group,
                'answer': data['answer'],
                'user': self.user
            }
        else:       
            group = data['group']
            # init user_answer
            group_obj = GroupExp.objects.get(name=self.group)
            users = group_obj.users.filter(is_staff=False)
            print('init user answer in group: ', group)
            for user in users:
                print(user.username)
                self.user_answer[user] = ""
                self.fake_user_answer[user] = ""
            event = {
                'type': 'start_quiz',
                'group': group,
                'count': self.count
            }

        async_to_sync(self.channel_layer.group_send)(
            self.group,
            event
        )


    def update_online_count(self):
        group_obj = GroupExp.objects.get(name=self.group)
        users = group_obj.users.filter(is_staff=False)
        online_count = users.count()
        users_group = group_obj.name
        event = {
            'type': 'online_count_handler',
            'online_count': online_count,
            'users': users,
            'group': users_group
        }
        async_to_sync(self.channel_layer.group_send)(
            self.group,
            event
        )
    
    def online_count_handler(self, event):
        online_count = event['online_count']
        users = event['users']
        # user's group
        group = event['group']
        print('online count: ', group, online_count, users)
        context = {
            'group': group,
            'online_count': online_count,
            'users': users
        }
        html = render_to_string('core/partials/online_users.html', context)
        self.send(text_data=html)
    
    def start_quiz(self, event):
        TempUserAnswer.objects.all().delete()
        group = event['group']
        self.count = event['count']
        context = {
            'group': group,
            'count': self.count,
            'question': 'Como te supo la gomita?',
            'answers': [
                'dulce',
                'picoso',
            ],
            'user': self.user,
            'stared': True
        }


        html = render_to_string('core/groupA.html', context)
        self.send(text_data=html)

        user_answer_context = {
            'group': group,
            'user_answer': self.user_answer,
            'count': self.count,
            'started': True
        }

        html = render_to_string('core/partials/control_panel.html', user_answer_context)
        self.send(text_data=html)
        
    def display_user_answer(self, event):
        group = event['group']
        answer = event['answer']
        user = event['user']

        self.user_answer[user] = answer
    

        context = {
            'group': group,
            'user_answer': self.user_answer
        }

        html = render_to_string('core/partials/user_answer_control.html', context)
        self.send(text_data=html)

       
    def display_fake_user_answer(self, event):
        username = event['user']
        answer = event['answer']
        self.fake_user_answer[username] =  answer

        for username, answer in self.fake_user_answer.items():
            print(username, answer)
      
        context = {
            'fake_user_answer': self.fake_user_answer,
            'request': self.scope['user']
        }
        
        print(username, self.scope['user']) 
        print(len(username), len(self.scope['user'].username))
            
        html = render_to_string('core/partials/user_answer_A.html', context)
        self.send(text_data=html)
         
        
    def next_question(self, event):
        group = self.scope['url_route']['kwargs']['group']
        group_obj = GroupExp.objects.get(name=group)
        self.fake_user_answer.clear()
        self.user_answer.clear()
        
        if self.count >= 1:
            context ={
                'count': -1,
            }
            html = render_to_string('core/partials/count.html', context)
            self.send(text_data=html)
            return
        else:
            self.count = event['count']
            context = {
                'count': self.count,
            }
            html = render_to_string('core/partials/count.html', context)
            self.send(text_data=html)

            html = render_to_string('core/partials/count_users.html', context)
            self.send(text_data=html)
    
class NormalConsumer(WebsocketConsumer):
    users = set()
    count = 0
    user_answer = defaultdict()
    fake_user_answer = defaultdict()
    MAX_TIME = 5
    time = MAX_TIME
    user_groups = defaultdict()

    time_flag = False

    def connect(self):
        self.user = self.scope['user']
        self.group= self.scope['url_route']['kwargs']['group']

         
        self.group_obj  = GroupExp.objects.get(name=self.group)
      
        

        if self.user not in self.group_obj.users.all():
            self.group_obj.users.add(self.user)
            print('users online on group: ', self.group_obj.name)
            print(self.group_obj.users.filter(is_staff=False))
    
            self.group_obj.save()


        async_to_sync(self.channel_layer.group_add)(
            self.group,
            self.channel_name
        )
        self.accept()
        self.users.add(self.user)
        group_obj = GroupExp.objects.get(name=self.group)
        self.update_online_count()
        
            
    def disconnect(self, close_code):
        self.users.discard(self.user)

        if self.user in self.group_obj.users.all():
        
            self.group_obj.users.remove(self.user)
            print(self.group_obj.users.all())
            self.group_obj.save()

        self.update_online_count()


        async_to_sync(self.channel_layer.group_discard)(
            self.group,
            self.channel_name
        )

    def receive(self, text_data):

        data = json.loads(text_data)
        print(self.count)
        print(data)
        group = ""
        event = defaultdict(str)

        if 'goto' in data:
            group = data['goto']
            print('goint to: ', group)
            event = {
                'type': 'goto_group',
                'group': group
            }
        elif 'name' in data:
            event = {
                'type': 'update_name',
                'name': data['name']
            }
        elif 'time' in data:
            print('time out')
            for user, answer in self.user_answer.items():
                user_obj = User.objects.get(username=user)
                TempUserAnswer.objects.create(user=user_obj, answer=answer, group=self.group_obj)
                UserAnswer.objects.create(user=user_obj, answer=answer, group=self.group_obj)
            print(TempUserAnswer.objects.all())
            sleep(3)
            event = {
                'type': 'next_question',
                'count': self.count + 1
            }
        elif 'answer' in data:
            group = data['group']
            for user, answer in self.user_answer.items():
                self.user_answer[user] = answer
                print(user, answer)
            event = {
                'type': 'display_user_answer',
                'group': group,
                'answer': data['answer'],
                'user': self.user
            }
        else:       
            group = data['group']
            # init user_answer
            group_obj = GroupExp.objects.get(name=self.group)
            users = group_obj.users.filter(is_staff=False)
            print('init user answer in group: ', group)
            for user in users:
                print(user.username)
                self.user_answer[user] = ""
                self.fake_user_answer[user] = ""
            event = {
                'type': 'start_quiz',
                'group': group,
                'count': self.count
            }

        async_to_sync(self.channel_layer.group_send)(
            self.group,
            event
        )


    def update_online_count(self):
        group_obj = GroupExp.objects.get(name=self.group)
        users = group_obj.users.filter(is_staff=False)
        online_count = users.count()
        users_group = group_obj.name
        event = {
            'type': 'online_count_handler',
            'online_count': online_count,
            'users': users,
            'group': users_group
        }
        async_to_sync(self.channel_layer.group_send)(
            self.group,
            event
        )
    
    def online_count_handler(self, event):
        online_count = event['online_count']
        users = event['users']
        # user's group
        group = event['group']
        print('online count: ', group, online_count, users)
        context = {
            'group': group,
            'online_count': online_count,
            'users': users
        }
        html = render_to_string('core/partials/online_users.html', context)
        self.send(text_data=html)
    
    def start_quiz(self, event):
        TempUserAnswer.objects.all().delete()
        group = event['group']
        self.count = event['count']
        context = {
            'group': group,
            'count': self.count,
            'question': 'Como te supo la gomita?',
            'answers': [
                'dulce',
                'picoso',
            ],
            'user': self.user,
            'stared': True
        }


        html = render_to_string('core/groupB.html', context)
        self.send(text_data=html)

        user_answer_context = {
            'group': group,
            'user_answer': self.user_answer,
            'count': self.count,
            'started': True
        }

        html = render_to_string('core/partials/control_panelB.html', user_answer_context)
        self.send(text_data=html)
        
    def display_user_answer(self, event):
        group = event['group']
        answer = event['answer']
        user = event['user']

        self.user_answer[user] = answer
    

        context = {
            'group': group,
            'user_answer': self.user_answer
        }

        html = render_to_string('core/partials/user_answer_B.html', context)
        self.send(text_data=html)

    def next_question(self, event):
        group = self.scope['url_route']['kwargs']['group']
        group_obj = GroupExp.objects.get(name=group)
        self.fake_user_answer.clear()
        self.user_answer.clear()
        
        if self.count >= 1:
            context ={
                'count': -1,
            }
            html = render_to_string('core/partials/count.html', context)
            self.send(text_data=html)
            return
        else:
            self.count = event['count']
            context = {
                'count': self.count,
            }
            html = render_to_string('core/partials/count.html', context)
            self.send(text_data=html)

            html = render_to_string('core/partials/count_users.html', context)
            self.send(text_data=html)  