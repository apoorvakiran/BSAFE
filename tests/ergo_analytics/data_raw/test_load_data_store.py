# -*- coding: utf-8 -*-
"""
Test Iterate Lab Inc.'s Data Storage.

@ author Jesper Kristensen
Copyright 2018-
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import os
import sys
import pandas as pd

# == we start by finding the project root:
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
while not os.path.split(ROOT_DIR)[1] == 'BSAFE':
    ROOT_DIR = os.path.dirname(ROOT_DIR)  # cd ../
sys.path.insert(0, ROOT_DIR)  # now insert into our Python path
# ==

from ergo_analytics.data_raw import LoadDataStore
from ergo_analytics import DataFilterPipeline
from ergo_analytics.filters import FixDateOscillations
from ergo_analytics.filters import DataCentering
from ergo_analytics.filters import ConstructDeltaValues
from ergo_analytics.filters import ZeroShiftFilter
from ergo_analytics.filters import WindowOfRelevantDataFilter
from ergo_analytics.filters import DataImputationFilter
from ergo_analytics.filters import QuadrantFilter
from ergo_analytics import ErgoMetrics


def test_load_data_storage_basic():
    """
    Very basic test that the connections work to AWS etc.

    :return:
    """

    ds = LoadDataStore()
    for raw_df, _ in ds.load(tester='john', project='johnson', all=False):
        assert len(raw_df) == 1750


def test_compute_score():
    """
    Tests the computation of a score of data from the Data Store.

    :return:
    """
    ds = LoadDataStore()

    for raw_df, _ in ds.load(tester='john', project='johnson', all=False):

        raw_df.dropna(how='all', inplace=True)

        # make some conversions:
        raw_df.iloc[:, 0] = pd.to_datetime(raw_df.iloc[:, 0])
        for j in range(1, 6 + 1):
            raw_df.iloc[:, j] = raw_df.iloc[:, j].astype(float)

        pipeline = DataFilterPipeline()
        # instantiate the filters:
        pipeline.add_filter(name='fix_osc', filter=FixDateOscillations())
        pipeline.add_filter(name='centering1', filter=DataCentering())
        pipeline.add_filter(name='delta_values', filter=ConstructDeltaValues())
        pipeline.add_filter(name='centering2', filter=DataCentering())
        pipeline.add_filter(name='zero_shift_filter', filter=ZeroShiftFilter())
        pipeline.add_filter(name='window', filter=WindowOfRelevantDataFilter())
        pipeline.add_filter(name='impute', filter=DataImputationFilter())
        pipeline.add_filter(name='quadrant_fix', filter=QuadrantFilter())
        # run the pipeline!
        structured_data_chunks = pipeline.run(on_raw_data=raw_df,
                                       with_format_code='5',
                                       use_subsampling=False)

        metrics = ErgoMetrics(list_of_structured_data_chunks=structured_data_chunks)
        metrics.compute()
        score = metrics.get_score()

        assert score is not None
        assert score >= 0 and score <= 7
