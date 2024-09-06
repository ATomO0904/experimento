from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', SingUpView.as_view(), name='signup'),
]
