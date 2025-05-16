import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Dashboards')
sns = boto3.client('sns')

SNS_TOPIC_ARN = 'arn:aws:sns:us-east-2:133058749238:NotifyManagers'

def lambda_handler(event, context):
    logger.info("Received Event: " + json.dumps(event, indent=2))

    try:
        dashboard_id = event['pathParameters']['dashboard_id']
        body = json.loads(event['body'])

        # Extract enhanced payload
        recipients_info = body.get('recipients', {})
        all_emails = recipients_info.get('emails', [])
        chunk_size = recipients_info.get('chunk_size', 500)
        batch_id = recipients_info.get('batch_id', 'default-batch')

        channels = body.get('channels', ["email"])  # Default to email

        logger.info(f"Sharing dashboard {dashboard_id} with {len(all_emails)} recipients in chunks of {chunk_size}")

        # Optional: Store batch_id in dashboard metadata instead of full list
        table.update_item(
            Key={'dashboard_id': dashboard_id},
            UpdateExpression='SET shared_with = :val1',
            ExpressionAttributeValues={':val1': [batch_id]}
        )

        # Publish recipient chunks to SNS
        for i in range(0, len(all_emails), chunk_size):
            chunk = all_emails[i:i + chunk_size]

            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=json.dumps({
                    "dashboard_id": dashboard_id,
                    "shared_with": chunk,
                    "channels": channels,
                    "batch_id": batch_id
                })
            )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': f'Dashboard shared with {len(all_emails)} managers in chunks.'})
        }

    except Exception as e:
        logger.error(f"[ERROR] {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
