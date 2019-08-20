# -*- coding: utf-8 -*-
"""
This file handles data loading from Elastic Search.

@ author Jesper Kristensen
Copyright 2018-
"""

__all__ = ["LoadElasticSearch"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import datetime
import pandas as pd
from elasticsearch import Elasticsearch
from . import BaseData


class LoadElasticSearch(BaseData):

    def __init__(self):
        """
        Constructor.
        """
        super().__init__()

        print("Data loading with Elastic Search object created!")

    def retrieve_data(self, mac_addresses=None,
                      from_date=None, till_date=None, hosts=None, index=None):
        """
        Retrieves the data from the Elastic Search database specified
        by "hosts". See the example under our "Test" folder for more details
        and/or the official website.

        Some good details on how to search the Elastic Search database can
        be found here:
        https://marcobonzanini.com/2015/02/02/how-to-query-elasticsearch-with-python/

        :param mac_addresses:
        :param from_date:
        :param till_date:
        :param hosts:
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

        # res = es.search(index=index, body={'query': {'match_all': {}}})

        all_data = []
        for mac_address in mac_addresses:

            this_device_documents = es.search(index=index, body={
                'query': {
                    'bool': {'must':
                                 [{"match_phrase": {"device": mac_address}}],
                             "filter": {
                                 "range": {
                                     "timestamp": {
                                         "gte": datetime.datetime.strptime(from_date, "%m/%d/%Y"),
                                         "lte": datetime.datetime.strptime(till_date, "%m/%d/%Y"),
                                     }
                                 }
                             }
                             }
                }
            })
            print("{} documents found for device {}".format(
                this_device_documents['hits']['total']['value'],
                mac_address))

            # get the data and turn into DataFrame:
            this_data = this_device_documents['hits']['hits']
            this_device_data = pd.concat(map(pd.DataFrame.from_dict,
                                             this_data), axis=1)['_source'].T
            this_device_data = this_device_data.reset_index(drop=True)

            # then append this device to the list holding all devices:
            all_data.append(this_device_data)

        data_all_devices = pd.concat(all_data)

        return data_all_devices
