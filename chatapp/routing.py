from .consumers import *
from django.urls import path

websocket_urlpatterns = [
    path(r"ws/sc-socket-server/<str:conversation_id>", ChatConsumer.as_asgi()),
    path(r"ws/sc-socket-server/receiver/<str:uid>", ConnectConsumer.as_asgi()),
    path(r"ws/asc-socket-server/", ChatAsyncConsumer.as_asgi()),
    
]