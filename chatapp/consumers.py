# consumer - basic unit of channels 
# they're like django views
# rather than just responding they can also initiate request to client while connected

import json
from channels.generic.websocket import WebsocketConsumer

class ChatConsumer(WebsocketConsumer):

    # handler called when client initially opens a connection & is about to finish websocket handshake 
    def connect(self):
        self.accept()

        self.send(json.dumps({
            'type': 'connection_established',
            'message': "you are now connected"
        }))

    def receive(self,text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        print('Msg: ',message)

    # send msg back to client whenever we receive a msg
    # json dumps is used to add type for frontend 
        self.send(text_data=json.dumps({
            "type": 'chat', 
            "message": message
        }))
