import os
import django
from django.core.asgi import get_asgi_application
import socketio # type: ignore
from datetime import datetime
from user.models import *
from asgiref.sync import sync_to_async

# Initialize AsyncServer with allowed CORS origins
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=['http://localhost:5173', 'http://127.0.0.1:5173']
)

@sio.event
async def connect(sid, environ):
    print('Client connected:', sid)

@sio.event
async def disconnect(sid):
    print('Client disconnected:', sid)

@sio.event
async def join_room(sid, data):
    print('the data comming in join room',data)
    room_id = data['room_id']
    await sio.enter_room(sid, room_id)
    print(f"{sid} joined room {room_id}")

@sio.event
async def send_message(sid, data):
    print('form the sendMessage ',data)
    room_id = data['room_id']
    message = data.get('message', '')  # Get message or default to empty string   
    image = data.get('image') 
    video = data.get('video') 
    audio = data.get('audio') 
    sender_id = data['sender_id']
    receiver_id = data['receiver_id']
    print(f"Message from {sender_id} to {receiver_id}: {message}")
    
    currenttimestamp = datetime.now().isoformat() + 'Z'  # UTC time in ISO 8601 format
    print('the data is ',currenttimestamp)


    await sio.emit('receive_message', {
        'message': message,
        'sender': sender_id,
        'receiver': receiver_id,
        'image': image,
        'video' : video,
        'audio' : audio,
        'timestamp': currenttimestamp  
    }, room=room_id)
    
@sio.event
async def audio_call(sid, data):
    print('form the audio_call ',data)
    room_id = data['room_id']
    message = data.get('message', '')  # Get message or default to empty string   
    sender_id = data['sender_id']
    receiver_id = data['receiver_id']
    print(f"Message from {sender_id} to {receiver_id}: {message}")

    await sio.emit('receive_message', {
        'message': message,
        'callId': data['callId'],
        'sender_id': sender_id,
        'receiver_id': receiver_id,
    }, room=room_id)
    
@sio.event
async def join_call_room(sid, data):
    print('the data comming in join room',data)
    room_id = data['room_id']
    callId = data['callId']
    await sio.enter_room(sid, room_id,callId)
    print(f"{sid} joined room {room_id}")
    
@sio.event
async def notification(sid,data):
    print('the notification',data)
    message = data['message']
    sender_id = data['sender_id']
    receiver_id = data['receiver_id']
    notification_type = data['notification_type']
    print(f"Message from {sender_id} to,{notification_type} {receiver_id}: {message}")
    
    # Use sync_to_async to save notification to the database
    await sync_to_async(Notification.objects.create)(
        sender_id=sender_id,
        receiver_id=receiver_id,
        message=message,
        notification_type=notification_type,
    )
    
    # Emit notification to the shop user
    await sio.emit('notification', {
        'message': message,
        'sender_id' : sender_id,
        'receiver_id': receiver_id,
        'notification_type':notification_type,
    })
    
    # print(f"Notification emitted to room {receiver_id}: {message}")


    
# Django and ASGI setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# ASGI application
django_asgi_app = get_asgi_application()
application = socketio.ASGIApp(sio, django_asgi_app)  # Combine Socket.IO and Django
