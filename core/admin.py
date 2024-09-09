from django.contrib import admin
from .models import GroupExp, UserAnswer, TempUserAnswer
# Register your models here.

admin.site.register(   GroupExp)
admin.site.register(   TempUserAnswer)
admin.site.register(   UserAnswer)
