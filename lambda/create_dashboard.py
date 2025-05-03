import json
import uuid
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Dashboards')

def lambda_handler(event, context):
    try:
        # Parse incoming JSON request body (from json string to usable python dictionary)
        body = json.loads(event['body'])
        
        # Generate a short, unique dashboard ID
        dashboard_id = f"dash_{str(uuid.uuid4())[:8]}"
        
        # Get current UTC time for created_at field
        created_at = datetime.utcnow().isoformat()
        
        # Prepare item to store in DynamoDB
        item = {
            'dashboard_id': dashboard_id,
            'created_by': body['created_by'],
            'name': body['name'],
            'headcount': body['headcount'],
            'payroll_cost': body['payroll_cost'],
            'overtime_hours': body['overtime_hours'],
            'shared_with': [],
            'created_at': created_at
        }

        table.put_item(Item = item)
        
        # Return the success response
        return {
            'statusCode' : 200,
            'body' : json.dumps({
                'dashboard_id': dashboard_id,
                'message': 'Dashboard created successfully'
            })
        }
        
    except Exception as e:
        # Return error response on failure
        return {
            'statusCode' : 500,
            'body': json.dumps({'error': str(e)})
        }