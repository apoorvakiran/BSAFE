# -*- coding: utf-8 -*-
"""
Tests the base data class.

================================
How to run (from project root):
================================
>> python -m pytest tests/ErgoAnalytics/RawData/test_base_data.py

@ author Jesper Kristensen
Copyright Iterate Labs, Inc. 2018-
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

from ErgoAnalytics.Data_Raw import BaseData


def test_base_data():

    bd = BaseData()

    assert bd.data_column_names is None

    #
    bd._data_column_names = ['n1', 'n2']
    assert bd.data_column_names == ['n1', 'n2']

    #
    bd._data_column_names = []
    assert bd.data_column_names == []
