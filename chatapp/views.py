from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import *
from .serializer import *

# Create your views here.

def lobby(request):
    return render(request,'chat/lobby.html')

class ConversationViewSet(ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer


class MessagesViewSet(ModelViewSet):
    queryset = Messages.objects.all()
    serializer_class = MessageSerializer
