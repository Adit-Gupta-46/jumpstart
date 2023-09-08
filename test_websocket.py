import socketio

BASE_URL = "http://localhost:5000"

# Create a SocketIO client
sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print('Connected to WebSocket server')

@sio.on('disconnect')
def on_disconnect():
    print('Disconnected from WebSocket server')

@sio.on('new_request_notification')
def on_new_request_notification(data):
    print('New request received:', data)
    # Add your WebSocket testing logic here

if __name__ == '__main__':
    sio.connect(BASE_URL)

    # Add your WebSocket testing logic here
    
    sio.wait()  # Wait for events