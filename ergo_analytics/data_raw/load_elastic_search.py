# -*- coding: utf-8 -*-
"""
This file handles data loading from an Elastic Search database.

@ author Jesper Kristensen
Copyright 2018- Iterate Labs, Inc.
"""

__all__ = ["LoadElasticSearch"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import os
import logging
import numpy as np
import pandas as pd
import elasticsearch
from elasticsearch_dsl import Search
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from constants import *
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

    def retrieve_data(self, mac_address=None, start_time=None, end_time=None,
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
        :param start_time:
        :param end_time:
        :param host:
        :param data_format_code: Which data format code are we using? This
        determines how the data is streaming in (such as, which order etc.)
        :return:
        """

        if not start_time or not end_time:
            raise Exception("Please provide both the start_time and the "
                            "end_time parameters!")

        if host is None:
            # used locally
            host = ["localhost:9200"]
            es = Elasticsearch(hosts=host,
                           use_ssl=False,
                           verify_certs=False)
        else:
            # used in staging and production on AWS to connect to ES
            # cluster on AWS:
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

        logger.debug("Established connection to the Elastic Search database.")

        data_all_devices = []
        try:
            search = Search(using=es, index=index).query("match",
                            device=mac_address).query("range",
                                        **{"timestamp": {"gte": start_time,
                                                         "lte": end_time}})
            search.count()  # used to test connection
        except elasticsearch.exceptions.ConnectionError:
            msg = "\nCommon Cause: Have you started the Elasticnet server?\n"
            logger.exception(msg)
            raise Exception(msg)

        device_data = []
        if search.count() == 0:
            logger.info("No documents found for device {}".format(mac_address))
            return None

        for hit in search.scan():
            # data is stored in the value key on elasticsearch
            data = [f"{hit['timestamp']},{hit['value']}",
                    hit['device'], hit['timestamp']]

            device_data.append(data)

        device_df = pd.DataFrame(device_data)
        device_df.columns = ['value', 'device', 'timestamp']
        logger.info("{} documents found for device.".format(len(device_df),
                                                            mac_address))
        data_all_devices.append(device_df)

        if len(data_all_devices) > 0:

            # get the correct data format code:
            try:
                data_format_code = str(data_format_code)
            except Exception:
                raise Exception("Please provide a valid data format code!")

            all_data = []
            data = pd.concat(data_all_devices, axis=0)['value'].values
            for datum in data:

                datapoint = self._load_datum(datum=datum,
                                        data_format_code=data_format_code)

                if datapoint is None:
                    continue

                all_data.append(datapoint)

            all_data = pd.concat(all_data)

            # cast data types once:
            all_data = self._cast_to_correct_types(all_data=all_data,
                                            data_format_code=data_format_code)

            return all_data

    @staticmethod
    def _load_datum(datum=None, data_format_code=None):
        """
        Loads a datum sent from the wearable.

        :param datum: The datum to load from the device.
        :return: date, numeric values, flag_load_ok
        """
        names = DATA_FORMAT_CODES[data_format_code]['NAMES']
        try:
            datum = datum.rstrip('\n').rstrip('\r').rstrip('\r').rstrip('\n')
            datum = np.asarray(datum.split(','))

            date = datum[0]
            values = datum[1:].astype(float)

            data = pd.DataFrame(data=np.append([date], values)).T
            data.columns = names
            if not data.shape[1] == len(names):
                # did not get the data we expected, do this because
                # the data can be cut off at times
                raise Exception

        except Exception:
            return None

        return data
