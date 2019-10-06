# -*- coding: utf-8 -*-
"""
Tests the Base Structured Data implementation.

================================
How to run (from project root):
================================
>> python -m pytest tests/ErgoAnalytics/StructuredData/test_baseStructuredData.py

Requirements:
    You will need pytest installed.

@ author Jesper Kristensen
Copyright Iterate Labs, Inc. 2018-
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

from ErgoAnalytics.StructuredData import BaseStructuredData


def test_simple():

    bsd = BaseStructuredData()

    assert bsd.name is None

    bsd = BaseStructuredData(name='some_name')

    assert bsd.name == 'some_name'
