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

from unittest.mock import MagicMock
from ErgoAnalytics.ergoMetrics import ErgoMetrics

data = MagicMock()
data.yaw = MagicMock(return_value=[1,2,3,4,2,8] * 2)
data.pitch = MagicMock(return_value=[1,2,3,4,2,8] * 2)
data.roll = MagicMock(return_value=[1,2,3,4,2,8] * 2)
# data._pitch = {'delta': [1,2,3,4,2,8] * 2}
# data._yaw = {'delta': [1,2,3,4,2,8] * 2}
# data._roll = {'delta': [1,2,3,4,2,8] * 2}

em = ErgoMetrics(structured_data=data)
em.compute()
