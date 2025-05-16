import json
import os
import boto3
import logging
from boto3.dynamodb.conditions import Key

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Setup DynamoDB
dynamodb = boto3.resource('dynamodb')
REPORT_TABLE = os.environ.get('REPORT_TABLE', 'DashboardEmailReport')
table = dynamodb.Table(REPORT_TABLE)

def lambda_handler(event, context):
    dashboard_id = event['queryStringParameters'].get('dashboard_id')

    if not dashboard_id:
        logger.warning("Missing dashboard_id in query parameters")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "dashboard_id is required"})
        }

    try:
        # Query by partition key
        response = table.query(
            KeyConditionExpression=Key('dashboard_id').eq(dashboard_id)
        )

        items = response.get('Items', [])

        # Summarize success/failure
        summary = {"success": 0, "failed": 0}
        for item in items:
            summary[item['status']] += 1

        logger.info(f"Returning email report for dashboard_id: {dashboard_id}, found {len(items)} entries")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "dashboard_id": dashboard_id,
                "summary": summary,
                "details": items
            })
        }

    except Exception as e:
        logger.error(f"Error while querying DashboardEmailReport: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
