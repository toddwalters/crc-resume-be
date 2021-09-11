# pylint: disable=redefined-outer-name,missing-docstring
import json
import os
import unittest
import boto3
import mock
from moto import mock_dynamodb2

DDB_TABLE_NAME = 'siteVisitCounterTable'
DEFAULT_REGION = 'us-east-1'

@mock_dynamodb2
@mock.patch.dict(os.environ, {'DB_TABLE_NAME': DDB_TABLE_NAME})
class TestLambdaFunction(unittest.TestCase):

    def setUp(self):
        self.dynamodb = boto3.client('dynamodb', region_name=DEFAULT_REGION)
        try:
            self.table = self.dynamodb.create_table(
                TableName=DDB_TABLE_NAME,
                KeySchema=[
                    {'KeyType': 'HASH', 'AttributeName': 'Site'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'Site', 'AttributeType': 'S'}
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
        except self.dynamodb.exceptions.ResourceInUseException:
            self.table = boto3.resource('dynamodb', region_name=DEFAULT_REGION).Table(DDB_TABLE_NAME)

    def test_update_data_to_db(self):
        from site_visit_counter import update_visit_counter
        self.table = boto3.resource('dynamodb', region_name=DEFAULT_REGION).Table(DDB_TABLE_NAME)
        res = update_visit_counter(self.table)
        visit_count = res['Attributes']['VisitCount']

        self.assertEqual(2, visit_count)
