from rest_framework import serializers
from .models import *

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields =('group_name','user1','user2')

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields ='__all__'