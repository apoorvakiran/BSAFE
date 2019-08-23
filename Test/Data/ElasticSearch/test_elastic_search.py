# -*- coding: utf-8 -*-
"""
Test the Elastic Search implementation in SAFE.

@ author Jesper Kristensen
Copyright 2018-
"""

__author__ = "Jesper Kristensen"
__version__ = "Alpha"

from Analytics import LoadElasticSearch


def test_retrieve():

    es = LoadElasticSearch()

    index = "iterate-labs-local-poc"
    es_data = es.retrieve_data(mac_addresses=['F6:12:3D:BD:DE:42',
                                              'F6:12:3D:BD:DE:52'],
                               from_date='06/28/2019',
                               till_date='07/08/2019',
                               hosts=None, index=index)

# bring the data in SAFE format...
# So needs to be in "Collection of Structured Data" format...
