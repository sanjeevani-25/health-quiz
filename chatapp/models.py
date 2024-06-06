from django.db import models
from roles.models import *
import uuid
# Create your models here.
class Conversation(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # group_name = models.UUIDField(unique=True,editable=True)
    group_name = models.CharField(max_length=100)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE , related_name='convo_sender')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE , related_name='convo_receiver')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'CONVERSATION'

class Messages(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE , related_name='messages')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='msgs_from_user')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='msgs_to_user')
    message = models.CharField(max_length=150)

    class Meta:
        db_table = 'MESSAGES'

'''
conversation 
- check if there else add (room id) then group id store (pk)
- one time connection between users
- created at
- updated at

messages
- created at 
- multiple conversations and msgs
- from
- to

'''

