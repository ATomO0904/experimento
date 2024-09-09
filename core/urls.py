from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('control/', views.control, name='control'),
    path('groupA/', views.groupA, name='groupA'),
    path('groupB/', views.groupB, name='groupB'),
    path('start-quiz-control/', views.start_quiz, name='start-quiz'),
    path('results/', views.results, name='results'),
    path('export-to-csv/', views.export_to_csv, name='export_to_csv'),
    path('controlB/', views.controlB, name='controlB'),
]

htmx_urls_patterns = [
    path('online-groupA/', views.online_groupA, name='online_groupA'),
    path('online-groupB/', views.online_groupB, name='online_groupB'),
]

urlpatterns += htmx_urls_patterns