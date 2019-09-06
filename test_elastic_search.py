# -*- coding: utf-8 -*-
"""
Test the Elastic Search implementation in SAFE.

@ author Jesper Kristensen
Copyright 2018-
"""

__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import json
from Analytics import Metrics
from Analytics import StructuredDataStreaming

# these are just some mac addresses that were created in generating
# the fake data (just so that we can test it out and grab a random valid one):
#with open("all_device_addresses.json", "r") as fd:
 #   mac_addresses_in_fake_database = json.load(fd)['addresses']
    # mac_addresses_in_fake_database = list of mac addresses (hypothetical)

# doesn't matter which exact address - just to test - so take the first:
####JACOB - Pulled in a test case data file, assigned address 
some_test_address = ['F6:12:3D:BD:DE:44']


def test_retrieve_elastic_search():
    """
    Test that we can retrieve data from elastic search and put in SAFE
    format for further downstream processing (metrics, reporter, ...).
    """
    index = "iterate-labs-local-poc"
    es_safe_data = StructuredDataStreaming(streaming_source='elastic_search',
                                           streaming_settings=
                                           {"mac_addresses": some_test_address,
                                            "from_date": '2019-03-01',
                                            "till_date": '2019-04-01',
                                            "hosts": None, "index": index,
                                            "data_format_code": "2"})
    # *note* the "streaming settings". This argument will be passed on to
    # the specific streamer in question...
    print("Data Loaded from Streaming:")
    print(es_safe_data.get_data())
    print(es_safe_data.pitch())
    mets = Metrics(es_safe_data)
    print(mets._strain)

test_retrieve_elastic_search()
print("All done!")

