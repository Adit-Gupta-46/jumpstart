'''
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

'''

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

def create_initial_request(dynamodb, requesting_user_email, request_time, request_location,
                   vehicle_make, vehicle_model, vehicle_color, vehicle_license_plate):
    # Access the Users table
    requests_table = dynamodb.Table('Requests')

    # Check if unfilfilled request from user already exists
    response = requests_table.get_item(
        Key={
            'requesting_user_email': requesting_user_email,
            'request_time': '0-' + request_time
        }
    )

    # Check if processing request from user already exists
    if 'Item' not in response:
        response = requests_table.get_item(
            Key={
                'requesting_user_email': requesting_user_email,
                'request_time': '1-' + request_time
            }
        )
    
    if 'Item' not in response:
        # Create the request item
        request_item = {
            'requesting_user_email': requesting_user_email,
            'request_time': '0-' + request_time,
            'request_location': request_location,
            'request_status': 'unfulfilled',
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

def assign_request(dynamodb, requesting_user_email, request_time, fulfilling_user_email,
                    fulfilling_location, fulfill_start_time):
    # Access the Users table
    requests_table = dynamodb.Table('Requests')

    # Check if unfulfilled request from user exists
    response = requests_table.get_item(
        Key={
            'requesting_user_email': requesting_user_email,
            'request_time': '0-' + request_time
        }
    )

    if 'Item' in response:
        # Update the request item
        response['Item'].update({
            'request_time': '1-' + request_time,
            'request_status': 'in progress',
            'fulfilling_user_email': fulfilling_user_email,
            'fulfilling_location': fulfilling_location,
            'fulfill_start_time': fulfill_start_time,
        })

        # Put the assigned item in the table
        requests_table.put_item(Item=response['Item'])
        # Delete the unassigned item in the table
        requests_table.delete_item(
            Key={
                'requesting_user_email': requesting_user_email,
                'request_time': '0-' + request_time
            }
        )
        print("Request updated successfully!")
        return True
    # else:
    return False

def complete_request(dynamodb, requesting_user_email, request_time, fulfill_end_time):
    # Access the Users table
    requests_table = dynamodb.Table('Requests')

    # Check if processing request from user exists
    response = requests_table.get_item(
        Key={
            'requesting_user_email': requesting_user_email,
            'request_time': '1-' + request_time
        }
    )

    if 'Item' in response:
        # Update the request item
        response['Item'].update({
            'request_time': '2-' + request_time,
            'request_status': 'fulfilled',
            'fulfill_end_time': fulfill_end_time,
        })

        # Put the completed item in the table
        requests_table.put_item(Item=response['Item'])
        # Delete the assigned item in the table
        requests_table.delete_item(
            Key={
                'requesting_user_email': requesting_user_email,
                'request_time': '1-' + request_time
            }
        )

        print("Request completed successfully!")
        return True
    # else:
    return False