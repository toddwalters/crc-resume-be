import boto3
import botocore
import logging
import json
import requests
import os

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)

DDB_TABLE_NAME = os.environ['DDB_TABLE_NAME']

def lambda_handler(event, context):
    log.debug("Event: {}".format(json.dumps(event, default=str)))
    response_data = {}
    response = {}
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DDB_TABLE_NAME)

    site = {
        'Site': 'myCRCSite',
        'VisitCount': 0
    }

    try:
        region = os.environ.get('AWS_REGION')
        resource_type = event['ResourceType']
        message = json.dumps(event, default=str)

        if event['RequestType'] == 'Delete':
            response_data['Delete'] = ('Delete RequestType was used')
            send(event, context, 'SUCCESS', response_data)
            log.info('Delete RequestType was used')
            log.debug(message)
            log.debug(json.dumps(response, default=str))
            return response
        if event['RequestType'] == 'Create':
            table.put_item(
                Item=site,
                ConditionExpression='attribute_not_exists(Site) AND attribute_not_exists(VisitCount)'
            )
            response_data['Create'] = ('Create RequestType was used')
            send(event, context, 'SUCCESS', response_data)
            log.info('Create RequestType was used')
            log.debug(json.dumps(response, default=str))
            return response
        else:
            response_data['Update'] = ('Update RequestType was used')
            send(event, context, 'SUCCESS', response_data)
            log.info('Update RequestType was used')
            log.debug(json.dumps(response, default=str))
            return response
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            response_data['Skip'] = ('Item Already Exists. Item Creation Not Required')
            send(event, context, 'SUCCESS', response_data)
            log.info('Item Already Exists. Item Creation Not Required!')
            log.debug(json.dumps(response, default=str))
        else:
            response_data['Error'] = ('Something went wrong')
            send(event, context, 'FAILED', response_data)
            log.info('Error! Something went wrong!')
            log.debug(json.dumps(response, default=str))
            raise

def send(event, context, responseStatus, responseData, physicalResourceId=None):
    responseUrl = event['ResponseURL']
    log.debug(responseUrl)
    responseBody = {}
    responseBody['Status'] = responseStatus
    responseBody['Reason'] = 'See the details in CloudWatch Log Stream: ' + context.log_stream_name
    responseBody['PhysicalResourceId'] = physicalResourceId or context.log_stream_name
    responseBody['StackId'] = event['StackId']
    responseBody['RequestId'] = event['RequestId']
    responseBody['LogicalResourceId'] = event['LogicalResourceId']
    responseBody['Data'] = responseData
    json_responseBody = json.dumps(responseBody, default=str)
    headers = {
        'content-type': '',
        'content-length': str(len(json_responseBody))
    }
    try:
        response = requests.put(responseUrl,
                                data=json_responseBody,
                                headers=headers)
        log.debug("Status code: " + response.reason)
        log.debug(json.dumps(responseBody, default=str))
    except Exception as e:
        log.debug("send(..) failed executing requests.put(..): " + str(e))
