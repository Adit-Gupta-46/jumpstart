import socketio

BASE_URL = "http://localhost:8088"

# Initialize the Socket.IO client
sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print('Connected to WebSocket server')

@sio.on('disconnect')
def on_disconnect():
    print('Disconnected from WebSocket server')

# Event handler for the "new_request_notification" event
@sio.on('new_request_notification')
def new_request_notification(data):
    print(f"Received a new request notification: {data}")

if __name__ == '__main__':
    # Connect to the Flask-SocketIO server
    sio.connect('http://localhost:8088')

    # You can send test data to the server if needed
    # For example, sending a request for a new notification
    # sio.emit('request_new_notification', {'some_key': 'some_value'}, namespace='/notifications')

    # Keep the client running to receive WebSocket notifications
    try:
        sio.wait()
    except KeyboardInterrupt:
        # Disconnect on Ctrl+C
        sio.disconnect()