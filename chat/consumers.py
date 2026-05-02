import json
import base64
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.files.base import ContentFile
from .models import Channel, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.channel_id = self.scope['url_route']['kwargs']['channel_id']
        self.room_group_name = f'chat_{self.channel_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'text')

        if message_type == 'reaction':
            emoji = data.get('emoji', '')
            message_id = data.get('message_id')
            reactions = await self.toggle_reaction(message_id, emoji)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'reaction_update',
                    'message_id': message_id,
                    'reactions': reactions,
                }
            )
            return

        content = data.get('content', '')
        file_data = data.get('file', None)
        file_name = data.get('file_name', '')

        message = await self.save_message(
            content=content,
            message_type=message_type,
            file_data=file_data,
            file_name=file_name
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': message.id,
                'content': message.content,
                'message_type': message_type,
                'file_url': message.file.url if message.file else None,
                'author': self.user.username,
                'author_avatar': self.user.get_avatar_url(),
                'author_url': f'/accounts/profile/{self.user.username}/',
                'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def reaction_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'reaction_update',
            'message_id': event['message_id'],
            'reactions': event['reactions'],
        }))

    @database_sync_to_async
    def toggle_reaction(self, message_id, emoji):
        from .models import Reaction
        message = Message.objects.get(id=message_id)
        reaction, created = Reaction.objects.get_or_create(
            message=message,
            user=self.user,
            emoji=emoji
        )
        if not created:
            reaction.delete()

        reactions = {}
        for r in Reaction.objects.filter(message=message):
            reactions[r.emoji] = reactions.get(r.emoji, 0) + 1
        return reactions

    @database_sync_to_async
    def save_message(self, content, message_type, file_data, file_name):
        channel = Channel.objects.get(id=self.channel_id)
        message = Message(
            channel=channel,
            author=self.user,
            content=content,
            message_type=message_type
        )
        if file_data and file_name:
            format, imgstr = file_data.split(';base64,')
            decoded = base64.b64decode(imgstr)
            message.file.save(file_name, ContentFile(decoded), save=False)
        message.save()
        return message


class DMConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.other_username = self.scope['url_route']['kwargs']['username']

        if not self.user.is_authenticated:
            await self.close()
            return

        users = sorted([self.user.username, self.other_username])
        self.room_group_name = f'dm_{users[0]}_{users[1]}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data.get('content', '')
        message_type = data.get('type', 'text')
        file_data = data.get('file', None)
        file_name = data.get('file_name', '')

        message = await self.save_dm(content, message_type, file_data, file_name)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': message.id,
                'content': message.content,
                'message_type': message_type,
                'file_url': message.file.url if message.file else None,
                'author': self.user.username,
                'author_url': f'/accounts/profile/{self.user.username}/',
                'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_dm(self, content, message_type, file_data, file_name):
        other_user = User.objects.get(username=self.other_username)
        message = Message(
            author=self.user,
            dm_recipient=other_user,
            content=content,
            message_type=message_type
        )
        if file_data and file_name:
            format, imgstr = file_data.split(';base64,')
            decoded = base64.b64decode(imgstr)
            message.file.save(file_name, ContentFile(decoded), save=False)
        message.save()
        return message