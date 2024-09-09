from django.urls import path
from .consumers import *

websocket_urlpatterns = [
    path('ws/control/<group>', ControlConsumer.as_asgi()),
    path('ws/normal/<group>', NormalConsumer.as_asgi()),
]
