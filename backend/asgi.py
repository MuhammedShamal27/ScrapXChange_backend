"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""
import os
import django
from django.core.asgi import get_asgi_application
import socketio

# Initialize AsyncServer with allowed CORS origins
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=['http://localhost:5173', 'http://127.0.0.1:5173']
)

# Define event handlers directly here
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

    await sio.emit('receive_message', {
        'message': message,
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'image': image,
        'video' : video,
        'audio' : audio,
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
    
# Django and ASGI setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# ASGI application
django_asgi_app = get_asgi_application()
application = socketio.ASGIApp(sio, django_asgi_app)  # Combine Socket.IO and Django






# import os

# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from user import routing


# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# # application = get_asgi_application()
# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             routing.websocket_urlpatterns
#         )
#     ),
# })
     
# @sio.event
# async def offer(sid, data):
#     print(f'Received offer data: {data}')
#     room_id = data['roomId']
#     offer = data['offer']
#     await sio.emit('offer', {'offer': offer}, room=room_id)

# @sio.event
# async def answer(sid, data):
#     print(f'Received answer data: {data}')
#     room_id = data['roomId']
#     answer = data['answer']
#     await sio.emit('answer', {'answer': answer}, room=room_id)

# @sio.event
# async def ice_candidate(sid, data):
#     print(f'Received ICE candidate data: {data}')
#     room_id = data['roomId']
#     candidate = data['candidate']
#     await sio.emit('ice-candidate', {'candidate': candidate}, room=room_id)