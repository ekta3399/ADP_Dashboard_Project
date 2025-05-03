import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Dashboards')
sns = boto3.client('sns')

SNS_TOPIC_ARN = 'arn:aws:sns:us-east-2:133058749238:NotifyManagers'  # actual ARN

def lambda_handler(event, context):
    try:
        dashboard_id = event['pathParameters']['dashboard_id']
        body = json.loads(event['body'])
        shared_with = body.get('shared_with', [])

        table.update_item(
            Key={'dashboard_id': dashboard_id},
            UpdateExpression='SET shared_with = :val1',
            ExpressionAttributeValues={':val1': shared_with}
        )

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps({
                'dashboard_id': dashboard_id,
                'shared_with': shared_with
            }),
            Subject="Dashboard Shared"
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Dashboard shared with managers'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
