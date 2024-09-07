# import socketio

# # Create a new AsyncServer instance
# sio = socketio.AsyncServer(async_mode='asgi')

# # Handle client connection
# @sio.event
# async def connect(sid, environ):
#     print('Client connected:', sid)

# # Handle client disconnection
# @sio.event
# async def disconnect(sid):
#     print('Client disconnected:', sid)

# # Handle incoming messages
# # Handle joining a room (when a shop or user joins a chat room)
# @sio.event
# async def join_room(sid, data):
#     room_id = data['room_id']
#     # Join the room with the given room_id
#     await sio.enter_room(sid, room_id)
#     print(f"{sid} joined room {room_id}")

# # Handle sending messages between clients
# @sio.event
# async def send_message(sid, data):
#     print('it is comming ')
#     room_id = data['room_id']
#     message = data['message']
#     sender_id = data['sender_id']  # ID of the sender (shop or user)
#     receiver_id = data['receiver_id']  # ID of the receiver (shop or user)

#     print(f"Message from {sender_id} to {receiver_id}: {message}")

#     # Emit the message to all participants in the room
#     await sio.emit('receive_message', {
#         'message': message,
#         'sender_id': sender_id,
#         'receiver_id': receiver_id
#     }, room=room_id)
