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

    # def batch_write(self, table_name, items):
    #     """
    #     Batch-write items to given table name, i.e., write a lot of items
    #     to the table at once.
    #
    #     :param items: list of items, each a dict, to insert.
    #     """
    #     dynamodb = self.conn
    #     table = dynamodb.Table(table_name)
    #     with table.batch_writer() as batch:
    #         for item in items:
    #             batch.put_item(Item=item)
    #     return True

    def register_data_in_database(self, **kwargs):
        """
        Insert meta-data for a new datum in the database.
        The actual data is stored in s3.
        """

        # TODO: Finish this part.

        import pdb
        pdb.set_trace()

        # meta_data = {'Project_ID': kwargs['project_id'],
        #            'Team_Name': kwargs['team_name'],
        #            'Project_Name': kwargs['project_name'],
        #            'IP': kwargs['ip'],
        #            'Hostname': kwargs['hostname'],
        #            'Country': kwargs['country'],
        #            'Location': kwargs['location'],
        #            'Timezone': kwargs['timezone'],
        #            'AWS_ACCESS_KEY': kwargs['aws_access_key'],
        #            'IP_INFO_TOKEN': kwargs['ip_info_token'],
        #            'Created_by_system_user_name':
        #                kwargs['created_by_system_user_name'],
        #            'Created_by_user': kwargs[
        #                'created_by_user'],
        #            }

        # dynamodb = self.conn
        # table = dynamodb.Table('Projects')
        # response = table.put_item(Item=project)
        # return response['ResponseMetadata']['HTTPStatusCode'] == 200

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

    def insert_project_if_not_exist(self, **kwargs):
        """
        Insert a new project to the database.
        """
        project = {'Project_ID': kwargs['project_id'],
                   'Team_Name': kwargs['team_name'],
                   'Project_Name': kwargs['project_name'],
                   'IP': kwargs['ip'],
                   'Hostname': kwargs['hostname'],
                   'Country': kwargs['country'],
                   'Location': kwargs['location'],
                   'Timezone': kwargs['timezone'],
                   'AWS_ACCESS_KEY': kwargs['aws_access_key'],
                   'IP_INFO_TOKEN': kwargs['ip_info_token'],
                   'Created_by_system_user_name':
                       kwargs['created_by_system_user_name'],
                   'Created_by_user': kwargs[
                       'created_by_user'],
                   }

        dynamodb = self.conn
        table = dynamodb.Table('Projects')
        response = table.put_item(Item=project)
        return response['ResponseMetadata']['HTTPStatusCode'] == 200

    def get_project_details(self, project_id=None):
        """
        Get the details of the project with the incoming ID.
        Returns a JSON with all information.
        """
        dynamodb = self.conn
        table = dynamodb.Table('Projects')

        response = table.query(
            KeyConditionExpression=Key('Project_ID').eq(project_id)
        )

        if 'Items' not in response:
            return

        assert len(response['Items']) == 1

        return response['Items'][0]

    def get_item(self, table_name=None, query_item=None):
        """
        Get an item given its key.
        """
        dynamodb = self.conn
        table = dynamodb.Table(table_name)
        response = table.get_item(
            Key=query_item
        )
        if 'Item' not in response:
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

    def check_that_project_exists(self, project_id=None):
        """
        Query for an item with or without using global secondary index.
        """
        dynamodb = self.conn
        table = dynamodb.Table('Projects')

        response = table.query(
            KeyConditionExpression=Key('Project_ID').eq(project_id)
        )

        return 'Items' in response

    def list_all_projects(self):
        """
        Lists all available projects in the Data Store.
        """
        dynamodb = self.conn
        table = dynamodb.Table('Projects')

        response = table.scan()

        return [] if not 'Items' in response else response['Items']

    def _create_project_table(self, table_name=None):
        """
        Creates the project table.
        """
        dynamodb = self.conn

        try:
            # since this is NOSQL we don't really have a schema strictly
            # defined, we just need a key below and then we can populate on
            # the fly as we want
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
            # since this is NOSQL we don't really have a schema strictly
            # defined, we just need a key below and then we can populate on
            # the fly as we want
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

    def create_if_not_exist(self):
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

        logger.debug("Project and Meta-data tables successfully created!")

    # def delete_item(self, table_name, item_key):
    #     """
    #
    #     """
    #     raise NotImplementedError("Implement me!")
    #     dynamodb = self.conn
    #     table = dynamodb.Table(table_name)
    #     response = table.delete_item(
    #         Key={item_key['name']: item_key['value']}
    #     )
    #     if response['ResponseMetadata']['HTTPStatusCode'] == 200:
    #         return True
    #     else:
    #         return False

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
