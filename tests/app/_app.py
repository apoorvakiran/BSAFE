# -*- coding: utf-8 -*-
"""
The idea here is to test "app.py"; so how the platform
will actually be called.

@ author Jesper Kristensen
Copyright 2018-
"""

__all__ = []
__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import os
import elasticsearch
from elasticsearch_dsl import Search
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import pandas as pd
import numpy as np


start_time = '2019-10-28T22:35:00Z'
end_time = '2019-10-28T22:45:00Z'
mac_address="F3:A8:7A:9E:6A:6F"
index = 'cassia-staging'
host = 'search-kinesis-cassia-test-ethsitlodguxwer6jtk7uozfkm.us-east-1.es.amazonaws.com'
awsauth = AWS4Auth('AKIAXTRZXZRUUGVCREU5','3h2BOZmyNs1KDcMDxA/y9wjfl/xRQ0Xq1g060dTH','us-east-1', 'es')
es = Elasticsearch(hosts=[{'host': host, 'port': 443}],http_auth=awsauth,use_ssl=True,verify_certs=True,connection_class=RequestsHttpConnection)
search = Search(using=es, index=index).query("match",device__keyword=mac_address).query("range",**{"timestamp": {"gte": start_time,"lte": end_time}}).sort("timestamp")

for hit in search.params(preserve_order=True).scan():
    print(f"{hit['device']} {hit['timestamp']},{hit['value']}")
