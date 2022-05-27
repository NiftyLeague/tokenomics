import boto3
from boto3.dynamodb.types import TypeDeserializer
import pickle

def extract(table_name):
    '''extracts all data from a DynamoDB table'''
    client = connect()
    payload = []

    response = client.scan(
        TableName=table_name
    )
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = client.scan(
            TableName='rentals',
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        data.extend(response['Items'])
    i = 0
    for item in data:
        payload.append(get_py_dict(item))
        i+=1
    print(f'successfully scanned {i} records')
    return payload

def connect():
    boto3.setup_default_session()
    client = boto3.client('dynamodb', 'us-east-1')
    return client

def get_py_dict(dyno_item):
    if dyno_item is None:
        return None
    deserializer = TypeDeserializer()
    result = {k: deserializer.deserialize(v) for k, v in dyno_item.items()}
    return replace_decimals(result)

def replace_decimals(obj):
    if isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj.keys():
            obj[k] = replace_decimals(obj[k])
        return obj
    elif isinstance(obj, boto3.dynamodb.types.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj

def save_file(file_name, data):
    import os
    if not os.path.exists('data'):
        os.makedirs('data')
    with open("data/" + file_name, "wb") as file:
        pickle.dump(data, file)

def refresh_table(table_name):
    data = extract(table_name)
    save_file(table_name, data)

if __name__ == "__main__":
    refresh_table('rentals')