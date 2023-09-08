import bcrypt

'''
SCHEMA:
Users:{
    first_name,
    last_name,
    email,
    password,
    helper_status
}
'''

def create_table(dynamodb):
    try:
        # Define table schemas
        users_table_schema = [
            {
                'AttributeName': 'email',
                'AttributeType': 'S'
            }
        ]
        # Create Users table
        dynamodb.create_table(
            TableName='Users',
            KeySchema=[
                {
                    'AttributeName': 'email',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=users_table_schema,
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
    except Exception as e:
        print(e)
        return None

def create_user(dynamodb, email, first_name, last_name, password, helper_status):
    # Access the Users table
    users_table = dynamodb.Table('Users')
    
    # Check if the user already exists
    response = users_table.get_item(
        Key={
            'email': email
        }
    )
    
    if 'Item' not in response:
        # Hash and salt the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # User does not exist, add the new user
        users_table.put_item(
            Item={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'password': hashed_password.decode('utf-8'),
                'helper_status': helper_status
            }
        )
        return True
    else:
        return False

def verify_user(dynamodb, email, password):
    users_table = dynamodb.Table('Users')
    response = users_table.get_item(Key={'email': email})
    if 'Item' in response:
        stored_hashed_password = response['Item']['password']
        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
            return True
    return False

def delete_user(dynamodb, email):
    users_table = dynamodb.Table('Users')
    response = users_table.delete_item(Key={'email': email})
    if 'ResponseMetadata' in response:
        return True
    return False