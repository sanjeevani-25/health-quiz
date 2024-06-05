from .consumers import *
from django.urls import path

websocket_urlpatterns = [
    path(r"ws/socket-server/", ChatConsumer.as_asgi()),
]