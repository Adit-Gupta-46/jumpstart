from flask import Flask, request, jsonify
import user_table
import request_table
import config
import boto3
from http import HTTPStatus

app = Flask(__name__)

'''
SCHEMA:
Users:{
    first_name,
    last_name,
    email,
    password,
    helper_status
}

Requests:{
    requesting_user_email,
    request_time,
    request_location,
    request_status,            // can be unfulfilled, processing, fulfilled
    vehicle_make,
    vehicle_model,
    vehicle_color,
    vehicle_license_plate,
    fulfilling_user_email,
    fulfilling_location,
    fulfill_start_time,
    fulfill_end_time,
}
'''

# Create a DynamoDB resource
dynamodb = boto3.resource('dynamodb', aws_access_key_id=config.aws_access_key_id, aws_secret_access_key=config.aws_secret_access_key, region_name='us-east-1')

# Create tables if not already existing
user_table.create_table(dynamodb)
request_table.create_table(dynamodb)

"""
USER TABLE API ENDPOINTS
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
REQUESTS TABLE API ENDPOINTS
"""
@app.route('/request', methods=['POST'])
def create_request():
    try:
        print("11111")
        data = request.get_json()
        print("22222")
        requesting_user_email = data['requesting_user_email']
        request_time = data['request_time']
        request_location = data['request_location']
        request_status = data['request_status']
        vehicle_make = data['vehicle_make']
        vehicle_model = data['vehicle_model']
        vehicle_color = data['vehicle_color']
        vehicle_license_plate = data['vehicle_license_plate']
        print("33333")

        if request_table.create_initial_request(dynamodb, requesting_user_email, request_time, request_location, request_status,
                          vehicle_make, vehicle_model, vehicle_color, vehicle_license_plate):
            return "Request created successfully", HTTPStatus.CREATED
        else:
            return "Request form user already exists", HTTPStatus.BAD_REQUEST
        
    except Exception as e:
        return str(e), HTTPStatus.INTERNAL_SERVER_ERROR

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)