from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class GroupExp(models.Model):
    name = models.CharField(max_length=100)
    max_users = models.IntegerField(default=8)
    users = models.ManyToManyField(User, related_name='users_in_group', null=True, blank=True)
    n_questions = models.IntegerField(default=12)
    
    def __str__(self):
        return self.name


class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)
    group = models.ForeignKey(GroupExp, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return self.user.username +  ' ' + self.answer

class TempUserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)
    group = models.ForeignKey(GroupExp, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username +  ' ' + self.answer