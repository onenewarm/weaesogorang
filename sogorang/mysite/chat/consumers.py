# chat/consumers.py
from re import M
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from home.models import *
from urllib.parse import urlparse





class ChatConsumer(WebsocketConsumer):
    
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

    # Receive message from WebSocket
    def receive(self, text_data):

        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        status = text_data_json['status']
        sender = text_data_json['sender']

        if 'action' in text_data_json and text_data_json['action'] == 'disconnect':
            message=""
            self.disconnect(0)
        if status == 'text':    
             # Save message in DB
            sender = text_data_json['sender']
            ch=ChatChannel.objects.get(roomName=self.room_name)
            ChatMessage.objects.create(channel=ch, message=message, sender=sender)
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                    {
                            'type': 'chat_message',
                            'status' : status,
                            'message': message,
                            'sender' : sender,

                    }
            )
        
        elif status == 'img':
             # Save message in DB
            k=ChatChannel.objects.filter(roomName=self.room_name).values('id')
            chatmessage = ChatMessage.objects.filter(channel__in=k).order_by('createTime').values('image')
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                    {
                            'type': 'chat_message',
                            'status' : status,
                            'message': chatmessage[len(chatmessage)-1]['image'],
                            'sender' : sender,

                    }
            )
    
       
        
    

        # Send message to room group


    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        status = event['status']
        sender = event['sender']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'status' : status,
            'message': message,
            'sender' : sender,
        }))