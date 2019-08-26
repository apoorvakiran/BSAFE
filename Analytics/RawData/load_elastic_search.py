# -*- coding: utf-8 -*-
"""
This file handles data loading from Elastic Search database.

@ author Jesper Kristensen
Copyright 2018-
"""

__all__ = ["LoadElasticSearch"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import datetime
import numpy as np
import pandas as pd
from elasticsearch import Elasticsearch
from Settings import *
from . import BaseData


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

        print("Data loading with Elastic Search object created!")

    def retrieve_data(self, mac_addresses=None, from_date=None, till_date=None,
                      hosts=None, index=None, data_format_code='3'):
        """
        Retrieves the data from the Elastic Search database specified
        by "hosts". See the example under our "Test" folder for more details
        and/or the official website.

        Some good details on how to search the Elastic Search database can
        be found here:
        "https://marcobonzanini.com/2015/02/02/
        how-to-query-elasticsearch-with-python/"

        :param mac_addresses:
        :param from_date:
        :param till_date:
        :param hosts:
        :param data_format_code: Which data format code are we using? This
        determines how the data is streaming in (such as, which order etc.)
        :return:
        """

        if not from_date or not till_date:
            raise Exception("Please provide both the from_date and the "
                            "till_date parameters!")

        if hosts is None:
            hosts = ["localhost:9200"]

        # connect to the database via provided hosts:
        es = Elasticsearch(hosts=hosts,
                           use_ssl=False,
                           verify_certs=False)

        mac_addresses = np.atleast_1d(mac_addresses).tolist()

        data_all_devices = []

        for ma in mac_addresses:
            # for each mac address/device

            # search_on_addresses = [{"match_phrase": {"device": ma}}
            #                        for ma in mac_addresses]

            documents_this_devie = es.search(index=index, body={
                'query': {
                    'bool': {'must': [{"match_phrase": {"device": ma}}],
                             "filter": {
                                 "range": {
                                     "timestamp": {
                                         "gte": datetime.datetime.strptime(
                                             from_date, "%m/%d/%Y"),
                                         "lte": datetime.datetime.strptime(
                                             till_date, "%m/%d/%Y"),
                                     }
                                 }
                             }
                             }
                }
            })

            print("{} documents found for device.".format(
                documents_this_devie['hits']['total']['value']))

            number_of_documents_retrieved = \
                documents_this_devie['hits']['total']['value']

            if number_of_documents_retrieved  == 0:
                continue
            elif number_of_documents_retrieved == 1:
                # Series needs conversion to DataFrame
                this_data = documents_this_devie['hits']['hits']
                device_data = pd.DataFrame(pd.concat(
                    map(pd.DataFrame.from_dict, this_data), axis=1)
                                           ['_source']).T
            else:

                # get the data and turn into DataFrame:
                this_data = documents_this_devie['hits']['hits']
                device_data = pd.concat(map(pd.DataFrame.from_dict,
                                            this_data), axis=1)['_source'].T

            data_this_device = device_data.reset_index(drop=True)
            data_all_devices.append(data_this_device)

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
                datum = datum.rstrip('\n').rstrip('\r').rstrip('\r'.rstrip('\n'))
                this_datum = np.asarray(datum.split(','))

                date = this_datum[0]
                values = this_datum[1:].astype(float)

                this_data = pd.DataFrame(data=np.append([date], values)).T
                this_data.columns = names

                all_data.append(this_data)

            all_data = pd.concat(all_data)

            return self._check_data(data=all_data, names=names, file_path=None,
                                    is_streaming=True)
