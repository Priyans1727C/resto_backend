import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import time

class MySyncConsumer(WebsocketConsumer):
    def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            print(user)
            print("anonymous user can't login")
            self.close()
        else:
            self.room_name = f"rm_user_{user.id}"
            self.room_group_name = f"user_{user.id}"
            
            async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
            self.accept()
            
       
            self.send(text_data=json.dumps({
                    'status': 'Connected',
                    'user': user.id,
                    'channel':self.room_group_name
                }))
        
    def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name
            )
        print(f"WebSocket disconnected with code: {close_code}")
        
    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', 'No message')
            for i in range(20):
                self.send(text_data=json.dumps({"count":i,"reply":message}))
                time.sleep(1)
        except json.JSONDecodeError:
            self.send(text_data=json.dumps({
                'error': 'Invalid JSON format',
                'status': 'error'
            }))
    
    def send_notification(self,event):
        self.send(text_data=json.dumps(event["data"]))