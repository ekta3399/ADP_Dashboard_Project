import json
import os
import requests

# Get API key from environment variable
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
# Use your verified sender address from SendGrid
SENDER_EMAIL = os.environ.get('SENDER_EMAIL') # Replace this with verified sender in AWS lambda environment variable 

SENDGRID_URL = 'https://api.sendgrid.com/v3/mail/send'

headers = {
    'Authorization': f'Bearer {SENDGRID_API_KEY}',
    'Content-Type': 'application/json'
}

def lambda_handler(event, context):
    for record in event['Records']:
        try:
            # Get the message published via SNS
            message = json.loads(record['Sns']['Message'])
            dashboard_id = message['dashboard_id']
            recipients = message['shared_with']

            for email in recipients:
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

                response = requests.post(SENDGRID_URL, headers=headers, json=payload)

                # If SendGrid fails, raise error
                if response.status_code >= 400:
                    print(f"[ERROR] Failed to send email to {email}: {response.text}")
                    raise Exception("SendGrid email failed")
                else:
                    print(f"[SUCCESS] Email sent to {email}")

        except Exception as e:
            print(f"[FATAL] Failed to process SNS message: {str(e)}")

        
