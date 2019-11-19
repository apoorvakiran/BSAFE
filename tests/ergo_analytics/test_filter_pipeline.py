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

import os
import sys

# == we start by finding the project root:
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
while not os.path.split(ROOT_DIR)[1] == 'BSAFE':
    ROOT_DIR = os.path.dirname(ROOT_DIR)  # cd ../
sys.path.insert(0, ROOT_DIR)  # now insert into our Python path
# ==

import pytest
import pandas as pd
from unittest.mock import MagicMock
from ergo_analytics.filters import ConstructDeltaValues
from ergo_analytics.filters import QuadrantFilter
from ergo_analytics import DataFilterPipeline
from ergo_analytics import ErgoMetrics


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


def test_running_pipeline():
    """
    Test running the data pipeline (the ETL).
    """

    data_format_code = '5'
    test_data_path = os.path.join(ROOT_DIR, "Demos",
                             f"demo-format-{data_format_code}",
                             "data_small.csv")
    test_data = pd.read_csv(test_data_path)

    #
    pipeline = DataFilterPipeline()
    pipeline.add_filter(name="construct-delta", filter=ConstructDeltaValues())

    list_of_structured_data_chunks = pipeline.run(on_raw_data=test_data,
                                    with_format_code=data_format_code,
                                    is_sorted=True,
                                    use_subsampling=True,
                                    subsample_size_index=10,
                                    number_of_subsamples=5,
                                    randomize_subsampling=False)

    assert len(list_of_structured_data_chunks) == 5

    for ix in range(5):
        # each chunk should contain 10 elements
        assert len(list_of_structured_data_chunks[ix].get_data()) == 10


def test_running_pipeline_2():
    """
    Test running the data pipeline (the ETL).
    """

    data_format_code = '5'
    test_data_path = os.path.join(ROOT_DIR, "Demos",
                             f"demo-format-{data_format_code}",
                             "data_small.csv")
    test_data = pd.read_csv(test_data_path)

    #
    pipeline = DataFilterPipeline()
    pipeline.add_filter(name="construct-delta", filter=ConstructDeltaValues())

    list_of_structured_data_chunks = pipeline.run(on_raw_data=test_data,
                                    with_format_code=data_format_code,
                                    is_sorted=True,
                                    use_subsampling=True,
                                    subsample_size_index=10,
                                    number_of_subsamples=1,
                                    randomize_subsampling=False)

    assert len(list_of_structured_data_chunks) == 1
    assert len(list_of_structured_data_chunks[0].get_data()) == 10


def test_running_pipeline_3():
    """
    Test running the data pipeline (the ETL).
    """

    data_format_code = '5'
    test_data_path = os.path.join(ROOT_DIR, "Demos",
                             f"demo-format-{data_format_code}",
                             "data_small.csv")
    test_data = pd.read_csv(test_data_path)

    #
    pipeline = DataFilterPipeline()
    pipeline.add_filter(name="construct-delta", filter=ConstructDeltaValues())

    list_of_structured_data_chunks = pipeline.run(on_raw_data=test_data,
                                    with_format_code=data_format_code,
                                    is_sorted=True,
                                    use_subsampling=True,
                                    subsample_size_index=8000,
                                    number_of_subsamples=4,
                                    randomize_subsampling=False)

    assert len(list_of_structured_data_chunks) == 4
    assert len(list_of_structured_data_chunks[0].get_data()) == len(test_data)
