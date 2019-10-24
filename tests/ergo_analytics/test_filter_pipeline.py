# -*- coding: utf-8 -*-
"""
Tests the Data Filter Pipeline.

============
How to run:
============
>> pytest tests/ErgoAnalytics/test_filter_pipeline.py

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
from ergo_analytics import DataFilterPipeline


def test_filter_pipeline():
    """
    Run a test to make sure the filter pipeline works.
    """

    filter1 = MagicMock()
    filter1._params = dict(param1=4)
    filter2 = MagicMock()
    #
    pipeline = DataFilterPipeline()
    pipeline.add_filter(name='test_filter1', filter=filter1)

    assert len(pipeline.view()) == 1
    assert list(pipeline.view().keys())[0] == 'test_filter1'

    pipeline.remove_filter(name='test_filter1')
    assert len(pipeline.view()) == 0

    pipeline.add_filter(name='test_filter1', filter=filter1)
    assert len(pipeline.view()) == 1
    assert list(pipeline.view().keys())[0] == 'test_filter1'

    pipeline.add_filter(name='test_filter2', filter=filter2)
    assert len(pipeline.view()) == 2
    assert list(pipeline.view().keys())[0] == 'test_filter1'
    assert list(pipeline.view().keys())[1] == 'test_filter2'

    assert pipeline.view()['test_filter1']._params == dict(param1=4)
