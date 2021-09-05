import logging
import json
import os
import boto3
from botocore.exceptions import ClientError

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)

DDB_TABLE_NAME = os.environ['DDB_TABLE_NAME']

def lambda_handler(event, context):
    log.info('Received event: {}'.format(json.dumps(event)))

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DDB_TABLE_NAME)

    log.info('Making call to update visit count table')

    try:
        response = update_visit_counter(table)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response


def update_visit_counter(table):
    log.info('Attempting to update visit counter table')

    try:
        updatedresponse = table.update_item(
            Key={
                'Site': 'myCRCSite'
            },
            UpdateExpression="set VisitCount = if_not_exists(VisitCount, :val0)",
            ExpressionAttributeValues={
                ':val0': 0
            },
            ReturnValues='UPDATED_NEW'
        )
        log.info('Table Counter Attribute currently set to %s', updatedresponse)
    except ClientError as e:
        print(e.response['Error']['Message'])
    try:
        updatedresponse = table.update_item(
            Key={
                'Site': 'myCRCSite'
            },
            UpdateExpression="set VisitCount = VisitCount + :val1",
            ExpressionAttributeValues={
                ':val1': 1
            },
            ReturnValues='UPDATED_NEW'
        )
        log.info('Table updated new counter value set to %s', updatedresponse)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return updatedresponse


def decrement_visit_counter(table):
    try:
        updatedresponse = table.update_item(
            Key={
                'Site': 'myCRCSite'
            },
            UpdateExpression="set VisitCount = VisitCount - :val1",
            ExpressionAttributeValues={
                ':val1': 1
            },
            ReturnValues='UPDATED_NEW'
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return updatedresponse
