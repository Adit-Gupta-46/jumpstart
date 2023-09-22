from gevent import monkey
monkey.patch_all()

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import user_table
import request_table
import config
import boto3
import json
from http import HTTPStatus
from queue import Queue
import threading
import time


app = Flask(__name__)
socketio = SocketIO(app, async_mode='gevent', websocket_path='/socket.io')  # Use gevent and specify the websocket_path

# Create a DynamoDB resource
dynamodb = boto3.resource('dynamodb', aws_access_key_id=config.aws_access_key_id, aws_secret_access_key=config.aws_secret_access_key, region_name='us-east-1')

# Create tables if not already existing
user_table.create_table(dynamodb)
request_table.create_table(dynamodb)

new_request_queue = Queue()

"""
HTTP USER TABLE API ENDPOINTS
"""
@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        email = data['email']
        first_name = data['first_name']
        last_name = data['last_name']
        password = data['password']
        helper_status = data['helper_status']

        if user_table.create_user(dynamodb, email, first_name, last_name, password, helper_status): 
            return "User created successfully", HTTPStatus.CREATED
        return "User already exists", HTTPStatus.BAD_REQUEST
        
    except Exception as e:
        return str(e), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/users/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        verification = user_table.verify_user(dynamodb, email, password)
        if verification:
            return "Login successful", HTTPStatus.OK
        return "Invalid credentials", HTTPStatus.UNAUTHORIZED
        
    except Exception as e:
        return str(e), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/users/<email>', methods=['DELETE'])
def delete_user(email):
    try:
        data = request.get_json()
        password = data['password']

        verification = user_table.verify_user(dynamodb, email, password)
        if verification:
            if user_table.delete_user(dynamodb, email):
                return "User deleted successfully", HTTPStatus.OK
        return "Invalid credentials", HTTPStatus.NOT_FOUND
        
    except Exception as e:
        return str(e), HTTPStatus.INTERNAL_SERVER_ERROR

"""
HTTP REQUESTS TABLE API ENDPOINTS
"""
@app.route('/requests', methods=['POST'])
def create_request():
    try:

        data = request.get_json()
        requesting_user_email = data['requesting_user_email']
        request_time = data['request_time']
        request_location = data['request_location']
        vehicle_make = data['vehicle_make']
        vehicle_model = data['vehicle_model']
        vehicle_color = data['vehicle_color']
        vehicle_license_plate = data['vehicle_license_plate']

        if request_table.create_initial_request(dynamodb, requesting_user_email, request_time, 
                                                request_location, vehicle_make, 
                                                vehicle_model, vehicle_color,
                                                vehicle_license_plate):
            # Emit a WebSocket event to notify clients about the new request
            request_data = requesting_user_email, request_time, request_location
            # socketio.emit('new_request_notification', json.dumps(request_data), namespace='/notifications')
            new_request_queue.put(request_data)
            print("12345678")
            # socketio.emit('new_request_notification', json.dumps(request_data))

            return "Request created successfully", HTTPStatus.CREATED
        else:
            return "Request from user already exists", HTTPStatus.BAD_REQUEST
        
    except Exception as e:
        return str(e), HTTPStatus.INTERNAL_SERVER_ERROR
    
@app.route('/requests/assign', methods=['POST'])
def assign_request():
    try:
        data = request.get_json()
        requesting_user_email = data['requesting_user_email']
        request_time = data['request_time']
        fulfilling_user_email = data['fulfilling_user_email']
        fulfilling_location = data['fulfilling_location']
        fulfill_start_time = data['fulfill_start_time']

        if request_table.assign_request(dynamodb, requesting_user_email, request_time, 
                                                fulfilling_user_email, fulfilling_location,
                                                fulfill_start_time):
            return "Request updated successfully", HTTPStatus.CREATED
        else:
            return "Existing unassigned request not found", HTTPStatus.BAD_REQUEST
        
    except Exception as e:
        return str(e), HTTPStatus.INTERNAL_SERVER_ERROR
    
@app.route('/requests/complete', methods=['POST'])
def complete_request():
    try:
        data = request.get_json()
        requesting_user_email = data['requesting_user_email']
        request_time = data['request_time']
        fulfill_end_time = data['fulfill_end_time']

        if request_table.complete_request(dynamodb, requesting_user_email, request_time, 
                                        fulfill_end_time):
            return "Request completed successfully", HTTPStatus.CREATED
        else:
            return "Request could not be completed", HTTPStatus.BAD_REQUEST
        
    except Exception as e:
        return str(e), HTTPStatus.INTERNAL_SERVER_ERROR

def handle_client_connect():
    while True:
        print("WebSocket notification handler started..................................................................")

        # Get a new request notification from the queue
        if not new_request_queue.empty:
            request_data = new_request_queue.get()
            if request_data:
                # Emit the notification via WebSocket
                print("jhfgjhgjhg", request_data)
                socketio.emit('new_request_notification', json.dumps(request_data))
        socketio.sleep(1)  # Sleep for 1 second before checking the queue again

# Create a thread to handle WebSocket notifications
notification_thread = threading.Thread(target=handle_client_connect)
notification_thread.start()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
    # The main program can continue running here
    try:
        while True:
            pass
    except KeyboardInterrupt:
        # If you want to stop the thread gracefully when you press Ctrl+C
        notification_thread.join()

