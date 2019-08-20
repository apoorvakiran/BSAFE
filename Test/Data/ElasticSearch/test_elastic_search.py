# -*- coding: utf-8 -*-
"""
Test the Elastic Search implementation in SAFE.

@ author Jesper Kristensen
Copyright 2018-
"""

__author__ = "Jesper Kristensen"
__version__ = "Alpha"

from Data import LoadElasticSearch


def test_retrieve():

    es = LoadElasticSearch()

    index = "iterate-labs-local-poc"
    es_data = es.retrieve_data(mac_addresses=['F6:12:3D:BD:DE:44'],
                               from_date='06/28/2019', till_date='07/01/2019',
                               hosts=None,
                               index=index)

    import pdb
    pdb.set_trace()
