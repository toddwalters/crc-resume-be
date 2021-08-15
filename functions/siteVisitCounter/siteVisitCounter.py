import logging
import json
import os
import boto3

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)

DDB_TABLE_NAME = os.environ['DDB_TABLE_NAME']

def lambda_handler(event, context):
    log.info('Received event: {}'.format(json.dumps(event)))

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DDB_TABLE_NAME)

    log.info('Making call to update visit count table')

    response = update_visit_counter(table)

    log.info('Table updated new counter value set to %s', response)

    return response


def update_visit_counter(table):
    log.info('Attempting to update visit counter table')

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
    return updatedresponse


def decrement_visit_counter(table):
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
    return updatedresponse
