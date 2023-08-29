import requests

BASE_URL = "http://localhost:5000"

# User creation test
user_data = {
    "email": "test@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "testpassword",
    "helper_status": True
}
response = requests.post(f"{BASE_URL}/users", json=user_data)
print("Create User:", response.status_code, response.text)

# User login test
login_data = {
    "email": "test@example.com",
    "password": "testpassword"
}
response = requests.post(f"{BASE_URL}/users/login", json=login_data)
print("Login User:", response.status_code, response.text)

# Request creation test
request_data = {
    "requesting_user_email": "test@example.com",
    "request_time": "2023-08-23T12:00:00",
    "request_location": "Some location",
    "request_status": "unfulfilled",
    "vehicle_make": "Toyota",
    "vehicle_model": "Camry",
    "vehicle_color": "Blue",
    "vehicle_license_plate": "ABC123"
}
response = requests.post(f"{BASE_URL}/request", json=request_data)
print("Create Request:", response.status_code, response.text)

# User deletion test
delete_data = {
    "password": "testpassword"
}
response = requests.delete(f"{BASE_URL}/users/test@example.com", json=delete_data)
print("Delete User:", response.status_code, response.text)