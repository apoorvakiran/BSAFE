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
from ergo_analytics.filters import ConstructDeltaValues
from ergo_analytics.filters import QuadrantFilter
from ergo_analytics import DataFilterPipeline
from ergo_analytics import ErgoMetrics


def test_with_metrics():

    data_format_code = '5'
    test_data_path = os.path.join(ROOT_DIR, "Demos",
                                  f"demo-format-{data_format_code}",
                                  "data_small.csv")
    test_data = pd.read_csv(test_data_path)

    #
    pipeline = DataFilterPipeline()
    pipeline.add_filter(name="construct-delta", filter=ConstructDeltaValues())
    pipeline.add_filter(name="quadrant", filter=QuadrantFilter())

    list_of_structured_data_chunks = pipeline.run(on_raw_data=test_data,
                                            with_format_code=data_format_code,
                                                  is_sorted=True,
                                                  use_subsampling=True,
                                                  subsample_size_index=8000,
                                                  number_of_subsamples=1,
                                                  randomize_subsampling=False)

    metrics = ErgoMetrics(
        list_of_structured_data_chunks=list_of_structured_data_chunks)

    metrics.compute()

    combined_score = metrics.get_score(name='total', combine='average')
    assert pytest.approx(combined_score, 0.00001) == 5.78668125


def test_some_of_the_chunks_have_no_data():

    data_format_code = '5'
    test_data_path = os.path.join(ROOT_DIR, "Demos",
                                  f"demo-format-{data_format_code}",
                                  "data_small.csv")
    test_data = pd.read_csv(test_data_path)

    #
    pipeline = DataFilterPipeline()
    pipeline.add_filter(name="construct-delta", filter=ConstructDeltaValues())
    pipeline.add_filter(name="quadrant", filter=QuadrantFilter())

    list_of_structured_data_chunks = pipeline.run(on_raw_data=test_data,
                                                  with_format_code=data_format_code,
                                                  is_sorted=True,
                                                  use_subsampling=True,
                                                  subsample_size_index=8000,
                                                  number_of_subsamples=4,
                                                  randomize_subsampling=False)

    list_of_structured_data_chunks[2] = []

    metrics = ErgoMetrics(
        list_of_structured_data_chunks=list_of_structured_data_chunks)

    metrics.compute()

    combined_score = metrics.get_score(name='total', combine='average')
    assert pytest.approx(combined_score, 0.00001) == 5.78668125


def test_some_of_the_chunks_have_none_data():

    data_format_code = '5'
    test_data_path = os.path.join(ROOT_DIR, "Demos",
                                  f"demo-format-{data_format_code}",
                                  "data_small.csv")
    test_data = pd.read_csv(test_data_path)

    #
    pipeline = DataFilterPipeline()
    pipeline.add_filter(name="construct-delta", filter=ConstructDeltaValues())
    pipeline.add_filter(name="quadrant", filter=QuadrantFilter())

    list_of_structured_data_chunks = pipeline.run(on_raw_data=test_data,
                                                  with_format_code=data_format_code,
                                                  is_sorted=True,
                                                  use_subsampling=True,
                                                  subsample_size_index=8000,
                                                  number_of_subsamples=4,
                                                  randomize_subsampling=False)

    list_of_structured_data_chunks[1] = []
    list_of_structured_data_chunks[2] = None

    metrics = ErgoMetrics(
        list_of_structured_data_chunks=list_of_structured_data_chunks)

    metrics.compute()

    combined_score = metrics.get_score(name='total', combine='average')
    assert pytest.approx(combined_score, 0.00001) == 5.78668125