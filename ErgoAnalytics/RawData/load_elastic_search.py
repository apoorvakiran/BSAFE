# -*- coding: utf-8 -*-
"""
This file handles data loading from Elastic Search database.
@ author Jesper Kristensen
Copyright 2018-
"""

__all__ = ["LoadElasticSearch"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import os
import datetime
import logging
import numpy as np
import pandas as pd
import elasticsearch
from elasticsearch_dsl import Search
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from Settings import *
from . import BaseData

logger = logging.getLogger()

class LoadElasticSearch(BaseData):
    """
    This code is responsible for loading "Elastic Search" database data.
    For example: We use it with streaming data:
    Data streams from the wearable to the cloud and then SAFE can query
    the elastic search database, analyze the data, and send back the results.
    """

    def __init__(self):
        """
        Construct the data loader.
        """
        super().__init__()

        logger.info("Data loading with Elastic Search object created!")

    def retrieve_data(self, mac_address=None, from_date=None, till_date=None,
                      host=None, index=None, data_format_code='3'):
        """
        Retrieves the data from the Elastic Search database specified
        by "host". See the example under our "Test" folder for more details
        and/or the official website.
        Some good details on how to search the Elastic Search database can
        be found here:
        "https://marcobonzanini.com/2015/02/02/
        how-to-query-elasticsearch-with-python/"
        :param mac_address:
        :param from_date:
        :param till_date:
        :param host: 
        :param data_format_code: Which data format code are we using? This
        determines how the data is streaming in (such as, which order etc.)
        :return:
        """

        if not from_date or not till_date:
            raise Exception("Please provide both the from_date and the "
                            "till_date parameters!")

        if host is None:
            # used locally
            host = ["localhost:9200"]
            es = Elasticsearch(hosts=host,
                           use_ssl=False,
                           verify_certs=False)
        else:
            # used in staging and production on AWS to connect to ES cluster on AWS
            awsauth = AWS4Auth(os.getenv('AWS_ACCESS_KEY'),
                               os.getenv('AWS_SECRET_KEY'),
                               os.getenv('AWS_REGION'), 'es')
            es = Elasticsearch(
                hosts=[{'host': host, 'port': 443}],
                http_auth=awsauth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection
            )

        import pdb
        pdb.set_trace()

        data_all_devices = []
        try:
            search = Search(using=es, index=index).query("match",
                        device=mac_address).query("range",
                        **{"timestamp": {"gte": from_date, "lte": till_date}})
            search.count()  # used to test connection
        except elasticsearch.exceptions.ConnectionError:
            raise Exception("\nHave you started the Elasticnet server?\n")

        device_data = []
        if search.count() == 0:
            logger.info("No documents found for device {}".format(mac_address))
            return None
        for hit in search.scan():
            data = [(hit['timestamp']+','+hit['data']), hit['device'], hit['timestamp']]
            device_data.append(data)
        device_df = pd.DataFrame(device_data)
        device_df.columns = ['data', 'device', 'timestamp']
        logger.info("{} documents found for device.".format(len(device_df), mac_address))
        data_all_devices.append(device_df)

        if len(data_all_devices) > 0:

            # get the correct data format code:
            try:
                data_format_code = str(data_format_code)
            except Exception:
                raise Exception("Please provide a valid data format code!")

            names = DATA_FORMAT_CODES[data_format_code]

            all_data = []
            data = pd.concat(data_all_devices, axis=0)['data'].values
            for datum in data:
                datum = datum.rstrip('\n').rstrip('\r').rstrip('\r').rstrip('\n')
                datum = np.asarray(datum.split(','))

                date = datum[0]
                values = datum[1:].astype(float)

                data = pd.DataFrame(data=np.append([date], values)).T
                data.columns = names

                all_data.append(data)

            all_data = pd.concat(all_data)

            return all_data
