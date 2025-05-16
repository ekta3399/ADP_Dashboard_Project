import json
import os
import requests
import boto3
from datetime import datetime
import logging

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'edith2744@gmail.com')
SENDGRID_URL = 'https://api.sendgrid.com/v3/mail/send'
IN_APP_TABLE = os.environ.get('IN_APP_TABLE', 'InAppNotifications')
REPORT_TABLE = os.environ.get('REPORT_TABLE', 'DashboardEmailReport')

# DynamoDB resources
dynamodb = boto3.resource('dynamodb')
in_app_table = dynamodb.Table(IN_APP_TABLE)
report_table = dynamodb.Table(REPORT_TABLE)

# Headers for SendGrid
headers = {
    'Authorization': f'Bearer {SENDGRID_API_KEY}',
    'Content-Type': 'application/json'
}

# Mock push notification
def send_push_notification(email):
    logger.info(f"[MOCK PUSH] Push notification sent to {email} (simulated)")

# Store in-app message in DynamoDB
def store_in_app_notification(email, dashboard_id):
    timestamp = datetime.utcnow().isoformat()
    in_app_table.put_item(Item={
        'user_email': email,
        'timestamp': timestamp,
        'dashboard_id': dashboard_id,
        'message': f"You’ve been granted access to dashboard {dashboard_id}."
    })
    logger.info(f"[IN-APP] Stored in-app notification for {email}")

# Store email report with batch_id
def store_email_report(dashboard_id, email, status, batch_id=None, error_message=None):
    item = {
        'dashboard_id': dashboard_id,
        'recipient_email': email,
        'status': status,
        'timestamp': datetime.utcnow().isoformat()
    }
    if batch_id:
        item['batch_id'] = batch_id
    if error_message:
        item['error_message'] = error_message

    report_table.put_item(Item=item)
    logger.info(f"[REPORT] Logged {status} for {email} (batch_id: {batch_id})")

# Main Lambda handler
def lambda_handler(event, context):
    for record in event['Records']:
        try:
            # Parse SNS message
            message = json.loads(record['Sns']['Message'])
            logger.info(f"[SNS MESSAGE RECEIVED] {json.dumps(message, indent=2)}")

            channels = [c.lower() for c in message.get('channels', ['email'])]
            dashboard_id = message['dashboard_id']
            recipients = message['shared_with']
            batch_id = message.get('batch_id')

            for email in recipients:
                # Send email
                if 'email' in channels:
                    payload = {
                        'personalizations': [
                            {
                                'to': [{'email': email}],
                                'subject': 'Dashboard Shared Notification'
                            }
                        ],
                        'from': {'email': SENDER_EMAIL},
                        'content': [
                            {
                                'type': 'text/plain',
                                'value': f"You’ve been granted access to dashboard {dashboard_id}."
                            }
                        ]
                    }

                    try:
                        response = requests.post(SENDGRID_URL, headers=headers, json=payload)

                        if response.status_code >= 400:
                            logger.error(f"[ERROR] Failed to send email to {email}: {response.text}")
                            store_email_report(dashboard_id, email, "failed", batch_id, response.text)
                        else:
                            logger.info(f"[SUCCESS] Email sent to {email}")
                            store_email_report(dashboard_id, email, "success", batch_id)

                    except Exception as e:
                        logger.error(f"[EXCEPTION] Email send failed for {email}: {str(e)}")
                        store_email_report(dashboard_id, email, "failed", batch_id, str(e))

                # Push notification
                if 'push' in channels:
                    send_push_notification(email)

                # In-app notification
                if 'in_app' in channels:
                    store_in_app_notification(email, dashboard_id)

        except Exception as e:
            logger.error(f"[FATAL] Failed to process SNS message: {str(e)}")
