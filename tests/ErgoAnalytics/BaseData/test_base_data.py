# -*- coding: utf-8 -*-
"""
Tests the base data class.

============
How to run:
============
>> pytest tests/ErgoAnalytics/test_base_data.py
============================= test session starts ==============================
platform darwin -- Python 3.7.1, pytest-4.0.2, py-1.7.0, pluggy-0.8.0
rootdir: /Users/johnjohnson/Dropbox/REI/Repos/SAFE_core, inifile:
plugins: remotedata-0.3.1, openfiles-0.3.1, doctestplus-0.2.0, arraydiff-0.3
collected 1 item

tests/ErgoAnalytics/test_base_data.py .                                  [100%]
[...]
===================== 1 passed, 4 warnings in 3.14 seconds =====================

Here we see that "1 passed" and we got no errors.

Requirements:
    You will need pytest installed.

@ author Jesper Kristensen
Copyright Iterate Labs, Inc. 2018-
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

from ErgoAnalytics.RawData import BaseData


def test_base_data():

    bd = BaseData()

    assert bd.data_column_names is None

    #
    bd._data_column_names = ['n1', 'n2']
    assert bd.data_column_names == ['n1', 'n2']

    #
    bd._data_column_names = []
    assert bd.data_column_names == []
