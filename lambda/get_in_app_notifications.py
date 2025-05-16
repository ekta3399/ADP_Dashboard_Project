import os
import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('IN_APP_TABLE', 'InAppNotifications')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    user_email = event['queryStringParameters'].get('user_email')
    
    if not user_email:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "user_email is required"})
    }
    
    response = table.query(
        KeyConditionExpression = Key('user_email').eq(user_email)
    )
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(response['Items'])
    }