# -*- coding: utf-8 -*-
"""
Test the Elastic Search implementation in SAFE.

@ author Jesper Kristensen
Copyright 2018-
"""

__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import json
from Analytics import StructuredDataStreaming

with open("all_device_addresses.json", "r") as fd:
    mac_addresses_in_fake_database = json.load(fd)['addresses']
    # mac_addresses_in_fake_database = list of mac addresses (hypothetical)

some_test_address = [mac_addresses_in_fake_database[0]]

def test_retrieve_elastic_search():
    """
    Test that we can retrieve data from elastic search and put in SAFE
    format for further downstream processing (metrics, reporter, ...).
    """

    index = "iterate-labs-local-poc"

    es_safe_data = StructuredDataStreaming(streaming_source='elastic_search',
                                           streaming_settings=
                                           {"mac_addresses": some_test_address,
                                            "from_date": '06/28/2019',
                                            "till_date": '07/08/2019',
                                            "hosts": None, "index": index})
    # *note* the "streaming settings". This argument will be passed on to
    # the specific streamer in question...

    print("Data Loaded from Streaming:")
    print(es_safe_data.get_data())

print("All done!")
