import os
import django
import socketio  # type: ignore
from datetime import datetime
from asgiref.sync import sync_to_async
import json

# Django and ASGI setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from django.core.asgi import get_asgi_application
from user.models import *  # Import after django.setup()
# Initialize AsyncServer with allowed CORS origins
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=[
        'http://74.179.83.230',
        'http://localhost:5173',
        'https://scrapxchange.store',
        'https://www.scrapxchange.store',
    ]
)

# Event handlers
@sio.event
async def connect(sid, environ):
    print('Client connected:', sid)

@sio.event
async def disconnect(sid):
    print('Client disconnected:', sid)

@sio.event
async def join_room(sid, data):
    print('Data received in join_room:', data)
    room_id = data['room_id']
    await sio.enter_room(sid, room_id)
    print(f"{sid} joined room {room_id}")

@sio.event
async def send_message(sid, data):
    print('Data received in send_message:', data)
    room_id = data['room_id']
    message = data.get('message', '')
    image = data.get('image')
    video = data.get('video')
    audio = data.get('audio')
    sender_id = data['sender_id']
    receiver_id = data['receiver_id']
    print(f"Message from {sender_id} to {receiver_id}: {message}")

    current_timestamp = datetime.now().isoformat() + 'Z'  # UTC time in ISO 8601 format
    print('Current timestamp:', current_timestamp)

    await sio.emit('receive_message', {
        'message': message,
        'sender': sender_id,
        'receiver': receiver_id,
        'image': image,
        'video': video,
        'audio': audio,
        'timestamp': current_timestamp
    }, room=room_id)

@sio.event
async def audio_call(sid, data):
    print('Data received in audio_call:', data)
    room_id = data['room_id']
    message = data.get('message', '')
    sender_id = data['sender_id']
    receiver_id = data['receiver_id']
    print(f"Audio call from {sender_id} to {receiver_id}: {message}")

    await sio.emit('receive_message', {
        'message': message,
        'callId': data['callId'],
        'sender_id': sender_id,
        'receiver_id': receiver_id,
    }, room=room_id)

@sio.event
async def join_call_room(sid, data):
    print('Data received in join_call_room:', data)
    room_id = data['room_id']
    callId = data['callId']
    await sio.enter_room(sid, room_id)
    print(f"{sid} joined call room {room_id}")



# ASGI application
django_asgi_app = get_asgi_application()
application = socketio.ASGIApp(sio, django_asgi_app) 
