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


def test_simple_system():
    basepath_raw_data = os.path.join(ROOT_DIR,
                                     "tests/system/fixtures/demo_data_only_deltas",
                                     "data_example1.csv")
    data_format_code = '4'  # in which format is the data coming to us?

    assert os.path.isfile(basepath_raw_data)

    put_structured_data_here = os.path.join(ROOT_DIR, "tests", "system")

    raw_data_loader = LoadDataFromLocalDisk()
    raw_data = raw_data_loader.get_data(path=basepath_raw_data,
                                        destination=put_structured_data_here,
                                        data_format_code=data_format_code)

    # now pass the raw data through our data filter pipeline:
    pipeline = DataFilterPipeline(is_streaming=False)
    structured_data = pipeline.run(raw_data=raw_data)

    metrics = ErgoMetrics(structured_data=structured_data)
    metrics.compute()

    print(structured_data.name)
    print(metrics.get_score(name='posture'))
    print(metrics.get_score(name='speed'))
