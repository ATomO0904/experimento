from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=100)
    max_users = models.IntegerField(default=8)
    n_questions = models.IntegerField(default=12)
    
    def __str__(self):
        return self.name

class UserInGroup(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.group.name + ' ' + self.user.username

class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)
    
    def __str__(self):
        return self.user.username + ' ' + self.question.text + ' ' + self.answer
