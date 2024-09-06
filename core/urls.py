from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('control/', views.control, name='control'),
    path('groupA/', views.groupA, name='groupA'),
    path('groupB/', views.groupB, name='groupB'),
    path('start-quiz-control/', views.start_quiz, name='start-quiz'),

    # API
]
