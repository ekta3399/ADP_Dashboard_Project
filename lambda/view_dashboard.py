import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Dashboards')

def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    return obj

def lambda_handler(event, context):
    try:
        dashboard_id = event['pathParameters']['dashboard_id']
        response = table.get_item(Key={'dashboard_id': dashboard_id})

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Dashboard not found'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps(convert_decimal(response['Item']))
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
