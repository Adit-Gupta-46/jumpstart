import requests

BASE_URL = "http://localhost:8088"

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
    "vehicle_make": "Toyota",
    "vehicle_model": "Camry",
    "vehicle_color": "Blue",
    "vehicle_license_plate": "ABC123"
}
response = requests.post(f"{BASE_URL}/requests", json=request_data)
print("Create Request:", response.status_code, response.text)

# Assign request test
assigning_data = {
    "requesting_user_email": "test@example.com",
    "request_time": "2023-08-23T12:00:00",
    "fulfilling_user_email": "fulfill@example.com",
    "fulfilling_location": "Updated location",
    "fulfill_start_time": "2023-08-23T12:30:00"
}
response = requests.post(f"{BASE_URL}/requests/assign", json=assigning_data)
print("Assign Request:", response.status_code, response.text)

# Complete request test
complete_data = {
    "requesting_user_email": "test@example.com",
    "request_time": "2023-08-23T12:00:00",
    "fulfill_end_time": "2023-08-23T13:00:00"
}
response = requests.post(f"{BASE_URL}/requests/complete", json=complete_data)
print("Complete Request:", response.status_code, response.text)

# User deletion test
delete_data = {
    "password": "testpassword"
}
response = requests.delete(f"{BASE_URL}/users/test@example.com", json=delete_data)
print("Delete User:", response.status_code, response.text)