# -*- coding: utf-8 -*-
"""
Test the Elastic Search implementation in SAFE.

Please run "es_load_test_data.py" first to generate the test data
to use with Elastic Search.

@ author Iterate Labs, Inc.
Copyright 2018-
"""

__author__ = "Iterate Labs, Inc."
__version__ = "Alpha"

import json
from ErgoAnalytics import ErgoMetrics
from ErgoAnalytics import StructuredDataStreaming

# these are just some mac addresses that were created in generating
# the fake data (just so that we can test it out and grab a random valid one):
with open("all_device_addresses.json", "r") as fd:
  mac_addresses_in_fake_database = json.load(fd)['addresses']

# doesn't matter which exact address - just to test - so take the first:
####JACOB - Pulled in a test case data file, assigned address
test_address = 'F6:12:3D:BD:DE:44'
# test_address = mac_addresses_in_fake_database[0]


def test_retrieve_elastic_search():
    """
    Test that we can retrieve data from elastic search and put in SAFE
    format for further downstream processing (metrics, reporter, ...).
    """
    index = "iterate-labs-local-poc"
    es_safe_data = StructuredDataStreaming(streaming_source='elastic_search',
                                           streaming_settings=
                                           {"mac_address": test_address,
                                            "from_date": '2019-09-28T00:00:00-05:00',
                                            "till_date": '2019-10-02T00:00:00-05:00',
                                            "host": None, "index": index},
                                           data_format_code='4')
    # *note* the "streaming settings". This argument will be passed on to
    # the specific streamer in question...
    print("Data Loaded from Streaming:")
    #print(es_safe_data.get_data())
    #print(es_safe_data.pitch())
    mets = ErgoMetrics(es_safe_data)
    print(mets._strain)

test_retrieve_elastic_search()
print("All done!")
