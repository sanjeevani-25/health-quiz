# consumer - basic unit of channels 
# they're like django views
# rather than just responding they can also initiate request to client while connected


import json
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

class ChatConsumer(WebsocketConsumer):

    # handler called when client initially opens a connection & is about to finish websocket handshake 
    def connect(self):
        self.room_group_name = 'test'

        # print('user : ',self.scope['user'])

        async_to_sync(self.channel_layer.group_add)(    
            self.room_group_name, self.channel_name
        )
        print("channel name: ",self.channel_name)
        self.accept()

        # self.send(json.dumps({
        #     'type': 'connection_established',
        #     'message': "you are now connected"
        # }))

    def receive(self,text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        print('Msg: ',message)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": 'chat.message', 
                "message": message
            }
        )

        print('Msg: ',message)
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