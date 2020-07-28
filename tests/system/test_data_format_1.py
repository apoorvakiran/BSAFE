# -*- coding: utf-8 -*-
"""
This is a simple system (end-to-end) going from raw data all the way
through reporting.

This code also serves as a "get started" for newcomers to BSAFE.

@ author Jesper Kristensen
Copyright Iterate Labs Inc. 2018-
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import os
from numpy import r_

from ergo_analytics.data_raw import LoadDataFromLocalDisk
from ergo_analytics import DataFilterPipeline
from ergo_analytics import ErgoMetrics
from ergo_analytics.metrics import AngularActivityScore
from ergo_analytics.filters import FixDateOscillations
from ergo_analytics.filters import DataCentering
from ergo_analytics.filters import ConstructDeltaValues
from ergo_analytics.filters import WindowOfRelevantDataFilter
from ergo_analytics.filters import DataImputationFilter
from ergo_analytics.filters import QuadrantFilter
from ergo_analytics.filters import ZeroShiftFilter
from constants import DATA_FORMAT_CODES


ROOT_DIR = os.path.abspath(os.path.expanduser("."))


def test_data_format_1():
    """
    Tests the BSAFE code on data with format code "1".
    The format code refers to what data is collected (its format: headers).
    """

    basepath_raw_data = os.path.join(
        ROOT_DIR, "Demos", f"demo-format-1", "data_small.csv"
    )

    assert os.path.isfile(basepath_raw_data)

    put_structured_data_here = os.path.join(ROOT_DIR, "tests", "system")

    raw_data_loader = LoadDataFromLocalDisk()
    raw_data = raw_data_loader.get_data(
        path=basepath_raw_data, destination=put_structured_data_here,
    )

    # now pass the raw data through our data filter pipeline:
    pipeline = DataFilterPipeline()
    # instantiate the filters:
    pipeline.add_filter(name="fix_osc", filter=FixDateOscillations())
    pipeline.add_filter(name="centering1", filter=DataCentering())
    pipeline.add_filter(name="delta_values", filter=ConstructDeltaValues())
    pipeline.add_filter(name="centering2", filter=DataCentering())
    pipeline.add_filter(name="zero_shift", filter=ZeroShiftFilter())
    pipeline.add_filter(name="window", filter=WindowOfRelevantDataFilter())
    pipeline.add_filter(name="impute", filter=DataImputationFilter())
    pipeline.add_filter(name="quadrant_fix", filter=QuadrantFilter())
    # run the pipeline!
    list_of_structured_data_chunks = pipeline.run(
        on_raw_data=raw_data,
        with_format_code=raw_data_loader.data_format_code,
        num_rows_per_chunk=100,
    )

    cols = list(list_of_structured_data_chunks[0].data_matrix.columns)
    assert cols == list(r_[DATA_FORMAT_CODES["1"]["NAMES"]])
    assert len(cols) == len(list(r_[DATA_FORMAT_CODES["1"]["NAMES"]]))

    metrics = ErgoMetrics(list_of_structured_data_chunks=list_of_structured_data_chunks)

    metrics.add(AngularActivityScore)
    metrics.compute()

    # we made it to here with this data format code so we should be good:
    assert len(metrics.get_score(name="AngularActivityScore")[0]) == 3
    assert metrics.get_score(name="AngularActivityScore")[0] is not None
