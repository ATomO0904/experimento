from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.template.loader import render_to_string
import json
from collections import defaultdict
# import User
from django.contrib.auth.models import User


class ControlConsumer(WebsocketConsumer):
    users = set()
    count = 0
    user_answer = defaultdict()
    fake_user_answer = defaultdict()

    def connect(self):
        self.user = self.scope['user']
        self.group = self.scope['url_route']['kwargs']['group']

        for user in self.users:
            print(user)

        async_to_sync(self.channel_layer.group_add)(
            self.group,
            self.channel_name
        )

        self.accept()
        self.users.add(self.user)
        self.update_online_count()
            
    def disconnect(self, close_code):
        self.users.discard(self.user)
        self.update_online_count()
        async_to_sync(self.channel_layer.group_discard)(
            self.group,
            self.channel_name
        )

    def receive(self, text_data):

        data = json.loads(text_data)
        print(data)
        group = ""
        self.count += 1
        event = defaultdict(str)
        
        if 'control' in data:
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
            event = {
                'type': 'display_user_answer',
                'group': group,
                'answer': data['answer'],
                'user': self.user
            }
        else:       
            group = data['group']
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
        online_count = len(self.users)
        
        users = list(self.users)
        event = {
            'type': 'online_count_handler',
            'online_count': online_count,
            'users': users
        }
        async_to_sync(self.channel_layer.group_send)(
            self.group,
            event
        )
    
    def online_count_handler(self, event):
        online_count = event['online_count']
        users = event['users']
        context = {
            'online_count': online_count,
            'users': users
        }
        html = render_to_string('core/partials/online_users.html', context)
        self.send(text_data=html)
    
    def start_quiz(self, event):
        group = event['group']
        count = event['count']
        self.user_answer[self.user] = ''
        self.fake_user_answer[self.user] = ''

        context = {
            'group': group,
            'count': count,
            'question': 'Como te supo la gomita?',
            'answers': [
                'dulce',
                'picoso',
            ],
            'user': self.user
        }

        html = render_to_string('core/partials/quiz.html', context)
        async_to_sync(self.channel_layer.group_send)(
            self.group,
            {
                'type': 'send_html',
                'html': html
            }
        )

        user_answer_context = {
            'group': group,
            'user_answer': self.user_answer
        }

        html = render_to_string('core/partials/user_answer_control.html', user_answer_context)
        self.send(text_data=html)

        # self.display_user_answer({
        #     'group': group,
        #     'answer': '',
        #     'user': self.user
        # })

    def display_user_answer(self, event):
        group = event['group']
        answer = event['answer']
        user = event['user']

        self.user_answer[user] = answer
        
        for user, answer in self.user_answer.items():
            print(user, answer)

        
        context = {
            'group': group,
            'user_answer': self.user_answer
        }
        # html = render_to_string('core/partials/user_answer_A.html', context)
        # async_to_sync(self.channel_layer.group_send)(
        #     self.group,
        #     {
        #         'type': 'send_html',
        #         'html': html
        #     }
        # )

        html = render_to_string('core/partials/user_answer_control.html', context)
        self.send(text_data=html)


    def send_html(self, event):
        html = event['html']
        self.send(text_data=html)

       
    def display_fake_user_answer(self, event):
    
        group = event['group']
        count = event['count']
        user = event['user']
        answer = event['answer']
        self.fake_user_answer[user] =  answer
        print(user, answer)
        context = {
            'fake_user_answer': self.fake_user_answer
        }
        
        html = render_to_string('core/partials/user_answer_A.html', context)
        self.send(text_data=html)
         
        
        # self.display_user_answer({
        #     'group': group,
        #     'answer': '',
        #     'user': user
        # })