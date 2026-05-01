import json
from channels.generic.websocket import AsyncWebsocketConsumer

class VoiceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.channel_id = self.scope['url_route']['kwargs']['channel_id']
        self.room_group_name = f'voice_{self.channel_id}'

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Informujemy innych że ktoś dołączył
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'username': self.user.username,
                'channel_name': self.channel_name,
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'username': self.user.username,
                'channel_name': self.channel_name,
            }
        )
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type')

        # Signaling WebRTC - przekazujemy offer/answer/candidate dalej
        if msg_type in ['offer', 'answer', 'ice-candidate']:
            target = data.get('target')  # channel_name konkretnego użytkownika
            await self.channel_layer.send(
                target,
                {
                    'type': 'signal',
                    'signal_type': msg_type,
                    'data': data.get('data'),
                    'sender': self.channel_name,
                    'username': self.user.username,
                }
            )

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'username': event['username'],
            'channel_name': event['channel_name'],
        }))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'username': event['username'],
            'channel_name': event['channel_name'],
        }))

    async def signal(self, event):
        await self.send(text_data=json.dumps({
            'type': event['signal_type'],
            'data': event['data'],
            'sender': event['sender'],
            'username': event['username'],
        }))