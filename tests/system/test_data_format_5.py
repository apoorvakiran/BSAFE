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
import sys

# == we start by finding the project root:
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
while not os.path.split(ROOT_DIR)[1] == 'BSAFE':
    ROOT_DIR = os.path.dirname(ROOT_DIR)  # cd ../
sys.path.insert(0, ROOT_DIR)  # now insert into our Python path
# ==

from ergo_analytics.data_raw import LoadDataFromLocalDisk
from ergo_analytics import DataFilterPipeline
from ergo_analytics import ErgoMetrics
from ergo_analytics.filters import FixDateOscillations
from ergo_analytics.filters import DataCentering
from ergo_analytics.filters import ConstructDeltaValues
from ergo_analytics.filters import WindowOfRelevantDataFilter
from ergo_analytics.filters import DataImputationFilter
from ergo_analytics.filters import QuadrantFilter
from constants import DATA_FORMAT_CODES


def test_data_format_5():

    data_format_code = '5'  # in which format is the data coming to us?

    basepath_raw_data = os.path.join(ROOT_DIR, "Demos",
                                     f"demo-format-{data_format_code}",
                                     "data.csv")

    assert os.path.isfile(basepath_raw_data)

    put_structured_data_here = os.path.join(ROOT_DIR, "tests", "system")

    raw_data_loader = LoadDataFromLocalDisk()
    raw_data = raw_data_loader.get_data(path=basepath_raw_data,
                                        destination=put_structured_data_here,
                                        data_format_code=data_format_code)

    # now pass the raw data through our data filter pipeline:
    pipeline = DataFilterPipeline()

    # instantiate the filters:
    # first, which columns to operate on for the various filters?
    numeric_columns = DATA_FORMAT_CODES[data_format_code]['NUMERICS']
    delta_columns = ['DeltaYaw', 'DeltaPitch', 'DeltaRoll']
    #
    f_date_oscillations = FixDateOscillations(columns='all')
    f_centering = DataCentering(columns=numeric_columns)
    f_construct_delta = ConstructDeltaValues(columns=numeric_columns)
    f_window = WindowOfRelevantDataFilter(columns=delta_columns)
    f_impute = DataImputationFilter(columns=numeric_columns)
    f_quadrant = QuadrantFilter(columns=delta_columns)

    pipeline.add_filter(name='fix_osc', filter=f_date_oscillations)
    pipeline.add_filter(name='centering1', filter=f_centering)
    pipeline.add_filter(name='delta_values', filter=f_construct_delta)
    pipeline.add_filter(name='centering2', filter=f_centering)
    pipeline.add_filter(name='window', filter=f_window)
    pipeline.add_filter(name='impute', filter=f_impute)
    pipeline.add_filter(name='quadrant_fix', filter=f_quadrant)

    pipeline.update_params(new_params=dict(data_format_code='5'))

    # run the pipeline!
    structured_data = pipeline.run(raw_data=raw_data)

    metrics = ErgoMetrics(structured_data=structured_data)
    metrics.compute()

    print(structured_data.name)
    print(metrics.get_score(name='posture'))
    print(metrics.get_score(name='speed'))
