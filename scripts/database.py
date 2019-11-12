# -*- coding: utf-8 -*-
"""
This database is built starting from:
https://github.com/santoshghimire/boto3-examples/blob/master/dynamodb.py
(MIT license) and expanded to meet our needs for the Iterate Labs Data Store.

@ author Jesper Kristensen
Copyright Iterate Labs, Inc 2018-
"""

__all__ = ["BackendDataBase"]
__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import logging
import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
import botocore

logger = logging.getLogger()


class BackendDataBase(object):
    """
    The backend database where projects are stored and meta-data associated
    with S3 data uploaded from the device.

    This is not meant to store any data from the device - that will live on
    S3 - this database keeps meta-data around.
    """

    _projects_table_name = None
    _meta_data_table_name = None

    def __init__(self, **kwargs):
        """
        Construct our database.

        Supply "region_name" as a keyword argument to select region.
        For example "us-east-1" which is the default.
        """
        region_name = kwargs.get('region_name', 'us-east-1')
        self.conn = boto3.resource('dynamodb', region_name=region_name)

        self._projects_table_name = 'Projects'  # keep projects here
        self._meta_data_table_name = 'Meta-Data'

    def batch_write(self, table_name, items):
        """
        Batch-write items to given table name, i.e., write a lot of items
        to the table at once.

        :param items: list of items, each a dict, to insert.
        """
        dynamodb = self.conn
        table = dynamodb.Table(table_name)
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
        return True

    def insert_item(self, table_name, item):
        """
        Insert an item to table.
        """

        dynamodb = self.conn
        table = dynamodb.Table(table_name)
        response = table.put_item(Item=item)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False

    def _insert_metadata(self):
        pass
        """
                {
                    'AttributeName': 'Project_ID',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'Project_Name',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'IP',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'Hostname',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'Country',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'Location',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'Timezone',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'Time_created_UTC',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'AWS_ACCESS_KEY',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'IP_INFO_TOKEN',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'Created_by_system_user_name',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'Created_by_user',
                    'AttributeType': 'S'
                },
        """

    def _insert_project(self):
        pass
        # {
        #     'AttributeName': 'Team_Name',
        #     'AttributeType': 'S'
        # },
        # {
        #     'AttributeName': 'Project_Name',
        #     'AttributeType': 'S'
        # },
        # {
        #     'AttributeName': 'IP',
        #     'AttributeType': 'S'
        # },
        # {
        #     'AttributeName': 'Hostname',
        #     'AttributeType': 'S'
        # },
        # {
        #     'AttributeName': 'Country',
        #     'AttributeType': 'S'
        # },
        # {
        #     'AttributeName': 'Location',
        #     'AttributeType': 'S'
        # },
        # {
        #     'AttributeName': 'Timezone',
        #     'AttributeType': 'S'
        # },
        # {
        #     'AttributeName': 'Time_created_UTC',
        #     'AttributeType': 'S'
        # },
        # {
        #     'AttributeName': 'AWS_ACCESS_KEY',
        #     'AttributeType': 'S'
        # },
        # {
        #     'AttributeName': 'IP_INFO_TOKEN',
        #     'AttributeType': 'S'
        # },
        # {
        #     'AttributeName': 'Created_by_system_user_name',
        #     'AttributeType': 'S'
        # },
        # {
        #     'AttributeName': 'Created_by_user',
        #     'AttributeType': 'S'
        # },

    def get_item(self, table_name, query_item):
        """
        Get an item given its key.
        """
        dynamodb = self.conn
        table = dynamodb.Table(table_name)
        response = table.get_item(
            Key=query_item
        )
        if not 'Item' in response:
            print(f"Element '{query_item}' not found!")

        item = response['Item']
        return item

    def update_item(self, table_name, key_dict, update_dict):
        """
        Update an item.
        PARAMS
        @table_name: name of the table
        @key_dict: dict containing the key name and val eg. {"uuid": item_uuid}
        @update_dict: dict containing the key name and val of
        attributes to be updated
        eg. {"attribute": "processing_status", "value": "completed"}
        """
        dynamodb = self.conn
        table = dynamodb.Table(table_name)
        update_expr = 'SET {} = :val1'.format(update_dict['attribute'])
        response = table.update_item(
            Key=key_dict,
            UpdateExpression=update_expr,
            ExpressionAttributeValues={
                ':val1': update_dict['value']
            }
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False

    def query_item(
        self, table_name, sort_key, partition_key,
        index_name=None, total_items=None, start_key=None,
        table=None
    ):
        """
        Query for an item with or without using global secondary index
        PARAMS:
        @table_name: name of the table
        @sort_key: Dict containing key and val of sort key
        e.g. {'name': 'uuid', 'value': '077f4450-96ee-4ba8-8faa-831f6350a860'}
        @partition_key: Dict containing key and val of partition key
        e.g. {'name': 'date', 'value': '2017-02-12'}
        @index_name (optional): Name of the Global Secondary Index
        """
        if not table:
            dynamodb = self.conn
            table = dynamodb.Table(table_name)
        sk = sort_key['name']
        skv = sort_key['value']
        pk = partition_key['name']
        pkv = partition_key['value']
        if not start_key:
            if index_name:
                response = table.query(
                    IndexName=index_name,
                    KeyConditionExpression=Key(sk).eq(skv) &
                    Key(pk).eq(pkv)
                )
            else:
                response = table.query(
                    KeyConditionExpression=Key(sk).eq(skv) &
                    Key(pk).eq(pkv)
                )
        else:
            if index_name:
                response = table.query(
                    IndexName=index_name,
                    KeyConditionExpression=Key(sk).eq(skv) &
                    Key(pk).eq(pkv),
                    ExclusiveStartKey=start_key
                )
            else:
                response = table.query(
                    KeyConditionExpression=Key(sk).eq(skv) &
                    Key(pk).eq(pkv),
                    ExclusiveStartKey=start_key
                )
        if not total_items:
            total_items = response['Items']
        else:
            total_items.extend(response['Items'])
        if response.get('LastEvaluatedKey'):
            start_key = response['LastEvaluatedKey']
            return_items = self.query_item(
                table_name=table_name, sort_key=sort_key,
                partition_key=partition_key, total_items=total_items,
                start_key=start_key, table=table
            )
            return return_items
        else:
            return total_items

    def scan_item(
        self, table_name, attr1, attr2,
        total_items=None, start_key=None,
        table=None
    ):
        """
        Scan for an item with two attributes
        NOTE: SCAN OPERATION SCANS THE WHOLE TABLE AND TAKES CONSIDERABLE
        AMOUNT OF TIME, CONSUMES HIGH READ THROUGHPUT.
        AVOID USING THIS AS MUCH AS YOU CAN.
        TRY CREATING INDEX AND USE QUERY IF POSSIBLE
        PARAMS:
        @table_name: name of the table
        @attr1: Dict containing key and val of first attribute
        e.g. {'name': 'uuid', 'value': '077f4450-96ee-4ba8-8faa-831f6350a860'}
        @attr2: Dict containing key and val of second attribute
        e.g. {'name': 'date', 'value': '2017-02-12'}
        """
        if not table:
            dynamodb = self.conn
            table = dynamodb.Table(table_name)

        a1 = attr1['name']
        a1v = attr1['value']
        a2 = attr2['name']
        a2v = attr2['value']
        if not start_key:
            response = table.scan(
                FilterExpression=Attr(a1).eq(a1v) &
                Attr(a2).eq(a2v)
            )
        else:
            response = table.scan(
                FilterExpression=Attr(a1).eq(a1v) &
                Attr(a2).eq(a2v),
                ExclusiveStartKey=start_key
            )
        if not total_items:
            total_items = response['Items']
        else:
            total_items.extend(response['Items'])
        if response.get('LastEvaluatedKey'):
            start_key = response['LastEvaluatedKey']
            return_items = self.query_item(
                table_name=table_name, attr1=attr1,
                attr2=attr2, total_items=total_items,
                start_key=start_key, table=table
            )
            return return_items
        else:
            return total_items

    def delete_item(self, table_name, item_key):
        """
        delete an item
        PARAMS
        @table_name: name of the table
        @item_key: dict containing key and val of sort key
        e.g. {'name': 'uuid', 'value': 'some-uuid-val'}
        """
        dynamodb = self.conn
        table = dynamodb.Table(table_name)
        response = table.delete_item(
            Key={item_key['name']: item_key['value']}
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False

    def _create_project_table(self, table_name=None):
        """
        Creates the project table.
        """
        dynamodb = self.conn

        try:
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': "Project_ID",
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'Project_ID',
                        'AttributeType': 'S'  # a string
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
        except Exception:
            msg = "Project table already exists, do not re-create..."
            logger.debug(msg)
            return

        if table:
            msg = "Database successfully created!"
            logger.debug(msg)
        else:
            msg = "There was an error creating the database on AWS!"
            logger.exception(msg)
            raise Exception(msg)

    def _create_meta_data_table(self, table_name=None):
        """
        Creates the table to store meta-data for wearable data uploaded
        to S3.
        """

        dynamodb = self.conn
        try:
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': "Data_ID",
                        'KeyType': 'HASH'  # hash means the partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'Data_ID',
                        'AttributeType': 'S'  # a string
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
        except Exception:
            msg = "Meta-Data table already exists, do not re-create..."
            logger.debug(msg)
            return

        if table:
            msg = "Database successfully created!"
            logger.debug(msg)
        else:
            msg = "There was an error creating the database on AWS!"
            logger.exception(msg)
            raise Exception(msg)

    def create(self):
        """
        Create the BackendDatabase which consists of a table holding
        project information and a table holding meta-data about data
        we upload to S3 from the device.
        """

        # Tables we need in the backend database:
        # projects in which we upload a set of data at once in the same
        # context.
        # store meta-data for data uploaded to S3 as well:
        self._create_project_table(table_name=self._projects_table_name)
        self._create_meta_data_table(table_name=self._meta_data_table_name)

    # def delete_all_items(self, table_name, hash_name):
    #     """
    #     Delete all items in a table by recreating the table.
    #     """
    #     dynamodb = self.conn
    #     try:
    #         table = dynamodb.Table(table_name)
    #         table.delete()
    #     except:
    #         print("Error in deletion. Table {} does not exist.".format(
    #                 table_name))
    #     # allow time for table deletion
    #     time.sleep(5)
    #     try:
    #         self.create_table(table_name, hash_name=hash_name)
    #     except:
    #         print("Error in creating table {}".format(table_name))
