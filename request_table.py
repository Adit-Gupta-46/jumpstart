"""
Schema:

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

"""

def create_table(dynamodb):
    try:
        # Define table schema
        requests_table_schema = [
            {
                'AttributeName': 'requesting_user_email',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'request_time',
                'AttributeType': 'S'
            }
        ]
        # Create Requests table
        dynamodb.create_table(
            TableName='Requests',
            KeySchema=[
                {
                    'AttributeName': 'requesting_user_email',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'request_time', # request_status(either unfulfilled, processing, or fulfilled) appended with request_time to sort by priority type and time
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=requests_table_schema,
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
    except Exception as e:
        print(e)
        return None

def create_initial_request(dynamodb, requesting_user_email, request_time, request_location, request_status,
                   vehicle_make, vehicle_model, vehicle_color, vehicle_license_plate):
    # Access the Users table
    requests_table = dynamodb.Table('Requests')
    # Check if request from user already exists
    response = requests_table.get_item(
        Key={
            'requesting_user_email': requesting_user_email,
            'request_time': request_time
        }
    )
    
    if 'Item' not in response:
        # Create the request item
        request_item = {
            'requesting_user_email': requesting_user_email,
            'request_time': request_time,
            'request_location': request_location,
            'request_status': request_status,
            'vehicle_make': vehicle_make,
            'vehicle_model': vehicle_model,
            'vehicle_color': vehicle_color,
            'vehicle_license_plate': vehicle_license_plate,
        }

        # Put the item in the table
        requests_table.put_item(Item=request_item)

        print("Request created successfully!")
        return True
    # else:
    return False