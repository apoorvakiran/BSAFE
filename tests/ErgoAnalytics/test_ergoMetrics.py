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

import pytest
from unittest.mock import MagicMock
from ErgoAnalytics.ergoMetrics import ErgoMetrics


def test_total_score():
    """
    Run a test to see if the total score matches what we expect.
    """

    data = MagicMock()
    data.yaw = MagicMock(return_value=[1,2,3,4,2,8] * 2)
    data.pitch = MagicMock(return_value=[1,2,3,4,2,8] * 2)
    data.roll = MagicMock(return_value=[1,2,3,4,2,8] * 2)

    em = ErgoMetrics(structured_data=data)
    em.compute()

    assert pytest.approx(em.get_score(name='total'), 0.0001) == 1.2256
