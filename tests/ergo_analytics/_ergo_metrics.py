# -*- coding: utf-8 -*-
"""
Tests the ErgoMetrics implementation.

============
How to run:
============
>> pytest tests/ErgoAnalytics/test_ergoMetrics.py

Requirements:
    You will need pytest installed.

@ author Jesper Kristensen
Copyright Iterate Labs, Inc. 2018-
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import os
import sys

import pytest
from unittest.mock import MagicMock
from ergo_analytics.ergo_metrics import ErgoMetrics


def test_total_score():
    """
    Run a test to see if the total score matches what we expect.
    """

    # pretend like this data in the "return_value" is what we collected
    data_chunks = MagicMock()
    data_chunks.get_data = MagicMock(
        return_value=[[1,2,3,4,2,8] * 2])

    em = ErgoMetrics(list_of_structured_data_chunks=data_chunks)
    em.compute()

    assert pytest.approx(em.get_score(name='total'), 0.0001) == 1.346153
    
    data_chunks = MagicMock()
    data_chunks.get_data = MagicMock(
        return_value=[[20, 40, 60, 80, 80, 80] * 2])
    
    em = ErgoMetrics(list_of_structured_data_chunks=data_chunks)
    em.compute()

    assert pytest.approx(em.get_score(name='total'), 0.0001) == 7
