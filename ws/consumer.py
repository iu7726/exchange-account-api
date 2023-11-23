# chat/consumers.py
import json, jwt, os, datetime

from channels.generic.websocket import AsyncWebsocketConsumer
from .scripts.OKEx import *
from libs_exchange_auth.TokenAuthentication import TokenAuthentication
from .scripts.OKEx import getClient

class SocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"account_{self.room_name}"
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        # url = "wss://ws.okx.com:8443/ws/v5/private"
        # subscribe(url)
        # Send message to room group
        # await self.channel_layer.group_send(
        #     self.room_group_name, {"type": "chat.message", "message": message}
        # )

        headers = data.get('headers')
        # print(headers)
        ogUserId = await self.checkCommunityToken(headers.get('Authorization'))
        result = ''
        if data.get('path') == 'okx_connect':
            self.client = await getClient(ogUserId)
            result = await self.client.subscribe(
                'wss://ws.okx.com:8443/ws/v5/private', 
                [
                    {"channel": "positions","instType":"ANY", "extraParams": json.dumps({"updateInterval": "1"})},
                    {"channel": "orders","instType":"ANY"}
                ],
                self
            )


        await self.send(text_data=json.dumps({"response": result}))
        # try:
            
        # except Exception as e:
        #     print('socket', e)
        #     await self.send(text_data=json.dumps({"response": 'socket error'}))

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
    
    async def checkCommunityToken(self, token) -> int:
        """Check the OG Community's Access Token.
        
        Args:
            request: The request object
        Returns:
            userId (int)
        """
        try:
            token = token.replace('Bearer ', '')
            
            ogUserInfo = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), 'HS256')
            now = datetime.datetime.now()
            if ogUserInfo['iat'] >= ogUserInfo['exp'] or now.timestamp() >= ogUserInfo['exp']:
                return 0
            return ogUserInfo['userId']
        except Exception as e:
            print(e)
            return 0