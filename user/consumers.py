from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from .models import ChatRoom, CustomUser, Message
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        print(f"Attempting to connect to room: {self.room_group_name}")

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print("WebSocket connection opened!")

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected: Room ID: {self.room_id}")
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        print('the data comming',data)
        message = data.get('message')
        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')

        print(f"Received message: {message} from {sender_id} to {receiver_id}")
        
        if not receiver_id:
            print("Receiver ID is None.")
            await self.send(text_data=json.dumps({
                'error': 'Receiver ID is missing'
            }))
            return

        # Save the message in the database
        new_message = await self.save_message(
            room_id=self.room_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            message=message
        )

        # Send the message to the WebSocket room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': new_message.sender.username,
                'receiver': new_message.receiver.username,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']

        print(f"Sending message: {message} from {sender} to {receiver}")

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'receiver': receiver,
        }))

    @sync_to_async
    def save_message(self, room_id, sender_id, receiver_id, message):
        try:
            room = ChatRoom.objects.get(id=room_id)
            sender = CustomUser.objects.get(id=sender_id)
            receiver = CustomUser.objects.get(id=receiver_id)
        except CustomUser.DoesNotExist:
            print(f"User with ID {receiver_id} does not exist.")
            return None

        # Check for duplicate messages
        existing_message = Message.objects.filter(
            room=room,
            sender=sender,
            receiver=receiver,
            message=message,
            timestamp__gte=timezone.now() - timedelta(seconds=5)  # Adjust the time window if needed
        ).first()

        if existing_message:
            print("Duplicate message detected, not saving.")
            return existing_message

        return Message.objects.create(
            room=room,
            sender=sender,
            receiver=receiver,
            message=message,
        )

