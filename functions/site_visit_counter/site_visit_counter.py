'''
Lambda used  to initialize and/or update DynamoDB Tab:qle item and item attribute
used to track number of visitors to a site
'''
import logging
import json
import os
import boto3
from botocore.exceptions import ClientError

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
LOG = logging.getLogger(__name__)
LOG.setLevel(LOG_LEVEL)

DDB_TABLE_NAME = os.environ.get('DDB_TABLE_NAME')

def lambda_handler(event, context):
    '''lambda handler used to update dynamoDB visitor count table'''

    LOG.info('%s', context)
    LOG.info('Received event: %s', json.dumps(event))

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DDB_TABLE_NAME)

    try:
        response = update_visit_counter(table)
    except ClientError as err:
        print(err.response['Error']['Message'])
    else:
        return response


def update_visit_counter(table):
    '''increment dynamo item counter attribute'''

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
        LOG.info('Table Counter Attribute currently set to %s', updatedresponse)
    except ClientError as err:
        print(err.response['Error']['Message'])
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
        LOG.info('Table updated new counter value set to %s', updatedresponse)
    except ClientError as err:
        print(err.response['Error']['Message'])
    else:
        return updatedresponse


def decrement_visit_counter(table):
    '''decrement dynamo item counter attribute'''
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
    except ClientError as err:
        print(err.response['Error']['Message'])
    else:
        return updatedresponse
