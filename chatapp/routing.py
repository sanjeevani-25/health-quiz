from .consumers import *
from django.urls import path

websocket_urlpatterns = [
    path(r"ws/sc-socket-server/", ChatConsumer.as_asgi()),
    path(r"ws/asc-socket-server/", ChatAsyncConsumer.as_asgi()),
    
]