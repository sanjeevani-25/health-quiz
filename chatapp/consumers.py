# consumer - basic unit of channels 
# they're like django views
# rather than just responding they can also initiate request to client while connected


import json
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import AnonymousUser
from .models import *
from .serializer import *
from django.contrib.auth import get_user_model
User = get_user_model()

class ConnectConsumer(WebsocketConsumer):

    # handler called when client initially opens a connection & is about to finish websocket handshake 
    def connect(self):
        # print(self.scope['headers'])
        sender = self.scope['user']
        print('sender (me) : ',self.scope['user'])

        if sender.is_anonymous:
            print("Anonymous userrrrr")
            self.close()

        else: 
            sender_id = sender.uid
            receiver = self.scope['url_route']['kwargs']['uid'].replace('-','')
            print("receiver  : ",receiver)
            receiver_id = User.objects.get(uid=receiver).uid


            sender = User.objects.get(uid=sender_id)
            receiver = User.objects.get(uid=receiver_id)

            try:
                conversation = Conversation.objects.get(user1=sender, user2=receiver)
                self.room_group_name = conversation.group_name
            except Conversation.DoesNotExist:
                try:
                    conversation = Conversation.objects.get(user2=sender, user1=receiver)
                    self.room_group_name = conversation.group_name
                except Conversation.DoesNotExist:
                    self.room_group_name = uuid.uuid4()
                    conversation = Conversation.objects.create(group_name=self.room_group_name, user1=sender, user2=receiver)

            # self.room_group_name  = (
            #     f'{sender_id}_{receiver_id}'
            #     if int(sender_id) > int(receiver_id)
            #     else f'{receiver_id}_{sender_id}'
            # )
            print("group name -->",self.room_group_name)

            print(conversation)

            async_to_sync(self.channel_layer.group_add)(    
                self.room_group_name, self.channel_name
            )
            # print("channel name: ",self.channel_name)

            self.accept()
            self.send(text_data=json.dumps({
                    "conversation_id": f'{conversation.uid}',
                    "url": f'/ws/sc-socket-server/{conversation.uid}'
                })
            )
            self.close()

            # self.scope['path'] = f'/ws/sc-socket-server/{self.room_group_name}'

class ChatConsumer(WebsocketConsumer):

    def connect(self):

        sender = self.scope['user']
        print('sender (me) : ',self.scope['user'])

        if sender.is_anonymous:
            print("Anonymous userrrrr")
            self.accept()
            self.send(text_data=json.dumps({
                "error": "cannot access - Anonymous user"
            }))
            self.close()
        
        else: 
            sender_id = sender.uid
            convo_id = self.scope['url_route']['kwargs']['conversation_id']
            conversation = Conversation.objects.get(uid=convo_id)
            print("user2 ",conversation.user2.uid)
            print("user1 ",conversation.user1.uid==sender_id)  

        if sender_id!=conversation.user1.uid or sender_id != conversation.user2.uid:
            self.accept()
            self.send(text_data=json.dumps({
            "error": "cannot access this chat"
            }))
            self.close()
        
        else:
            self.accept()
            self.get_previous_chats(convo_id)


    def get_previous_chats(self, id):
        previous_chats = Messages.objects.filter(conversation=id).order_by('-created_at')
        
        data = {
            "previous_messages": self.prev_msgs(previous_chats)
        }
        self.send(text_data=json.dumps(data))

    def prev_msgs(self, chats):
        result=[]
        for chat in chats:
                result.append({
                    'Date and time': f'{chat.created_at}',
                    'author':chat.from_user.first_name,
                    'message':chat.message,
                })
        return result
            
    def receive(self,text_data):

        sender_id = self.scope["user"].uid
        convo_id = self.scope['url_route']['kwargs']['conversation_id']
        conversation = Conversation.objects.get(uid=convo_id)
        if sender_id==conversation.user1:
            receiver_id = conversation.user2.uid
        else:
            receiver_id = conversation.user1.uid
        
        self.room_group_name = conversation.group_name

        data = {
            "from_user" : sender_id,
            "to_user" : receiver_id,
            "conversation": convo_id,
            "message": text_data
        }
        print(len(text_data))

        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)
            # self.send(text_data=serializer.errors)
        print("channelname ", self.channel_name)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": 'chat.message', 
                "message": text_data
            }
        )
        self.get_previous_chats(convo_id)

        ''' 
        - send msg back to client whenever we receive a msg 
        - json dumps is used to add type for frontend 
        '''
        # self.send(text_data=json.dumps({
        #     "type": 'chat', 
        #     "message": message
        # }))


    def chat_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            "type": 'chat', 
            "message": message
        }))



class ChatAsyncConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_group_name = 'test'

        await self.channel_layer.group_add(self.room_group_name,self.channel_name)
        print("channel name: ",self.channel_name)
        await self.accept()

    async def receive(self,text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        print('Msg: ',message)

        await self.channel_layer.group_send(self.room_group_name,{
                "type": 'chat.message', 
                "message": message
            })
        
        print('Msg: ',message)

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            "type": 'chat', 
            "message": message
        }))