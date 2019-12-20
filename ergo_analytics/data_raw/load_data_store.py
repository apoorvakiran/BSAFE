# -*- coding: utf-8 -*-
"""
Load data from Iterate Labs' Data Storage.

@ author Jesper Kristensen
Copyright 2018-
"""

__all__ = ["LoadDataStore"]
__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import os
import sys
import boto3
import numpy as np
import pandas as pd

# == we start by finding the project root:
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
while not os.path.split(ROOT_DIR)[1] == 'BSAFE':
    ROOT_DIR = os.path.dirname(ROOT_DIR)  # cd ../
sys.path.insert(0, ROOT_DIR)  # now insert into our Python path
sys.path.insert(0, os.path.join(ROOT_DIR, 'scripts'))
# ==

import logging

from tempfile import mkdtemp
import subprocess
from . import BaseData

logger = logging.getLogger()


class LoadDataStore(BaseData):
    """
    Loads data from Iterate Labs' Data Store.
    """

    def __init__(self):

        super().__init__()

        logger.info("Data loading from Data Store object created!")

    def iterate_over_files(self, tester=None, project=None):
        """
        Iterates over all files for this tester and project in
        order of when the file was created (from most recent first).
        """

        s3 = boto3.resource('s3')
        my_bucket = s3.Bucket('datastore.iteratelabs.co')

        s3 = boto3.client('s3')

        # get the meta-data to find time-created:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('Meta-Data')
        from boto3.dynamodb.conditions import Key

        # first collect dates created to sort by that:
        all_data_id = []
        all_dates_created = []
        for this_file in my_bucket.objects.filter(Prefix=f'{tester}/{project}'):
            data_id = this_file.key

            # find when the data was created - let's query the meta data table!
            response = table.query(
                KeyConditionExpression=Key('Data_ID').eq(data_id)
            )
            if 'Items' not in response:
                print(f"No data found for tester: '{tester}' under "
                      f"project: '{project}'")

            assert len(response['Items']) == 1
            datum_meta_data = response['Items'][0]
            date_created = datum_meta_data['date-created']

            all_data_id.append(data_id)
            all_dates_created.append(pd.to_datetime(date_created))

        ixs = np.argsort(all_dates_created)[::-1]

        all_dates_created = np.asarray(all_dates_created)[ixs]
        all_data_id = np.asarray(all_data_id)[ixs]

        for when_created, data_path in zip(all_dates_created, all_data_id):
            # now download the data directly in ram:
            this_data = s3.get_object(Bucket='datastore.iteratelabs.co',
                                      Key=data_path)
            df = pd.read_csv(this_data['Body'])  # pandas DataFrame
            yield df

    def load(self, tester=None, project=None):
        """
        Loads the latest file from the data store which is stored
        for the given tester and under the given project.
        """
        for df in self.iterate_over_files(tester=tester, project=project):
            # just take the most recent file:
            return df
