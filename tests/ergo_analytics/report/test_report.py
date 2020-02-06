# -*- coding: utf-8 -*-
"""
Tests the report implementation.

@ author Jesper Kristensen
Copyright Iterate Labs, Inc. 2018-
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import os
import sys
import pandas as pd
import pytest

from ergo_analytics import ErgoMetrics
from ergo_analytics import DataFilterPipeline
from ergo_analytics.filters import ConstructDeltaValues
from ergo_analytics.filters import QuadrantFilter
from ergo_analytics import ErgoReport
from ergo_analytics.metrics import AngularActivityScore
from ergo_analytics.metrics import PostureScore

ROOT_DIR = os.path.abspath(os.path.expanduser('.'))


def test_report():


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
    metrics.add(AngularActivityScore, name='activity')
    metrics.add(PostureScore, name='posture')
    metrics.compute()

    reporter = ErgoReport(ergo_metrics=metrics)

    string = reporter.to_string()

    assert pytest.approx(string['activity'][0][0], 0.00001) == 1.0738636363636365
    assert pytest.approx(string['activity'][0][1], 0.00001) == 1.0738636363636365
    assert pytest.approx(string['activity'][0][2], 0.00001) == 0.4375

    assert len(string['activity'][1]) == 0
    assert len(string['activity'][2]) == 0

    assert pytest.approx(string['activity'][3][0], 0.00001) == 1.0738636363636365
    assert pytest.approx(string['activity'][3][1], 0.00001) == 1.0738636363636365
    assert pytest.approx(string['activity'][3][2], 0.00001) == 0.4375

    assert pytest.approx(string['posture'][0][0], 0.00001) == 0.08750000000000001
    assert pytest.approx(string['posture'][0][1], 0.00001) == 0.08750000000000001
    assert pytest.approx(string['posture'][0][2], 0.00001) == 0.08750000000000001

    assert len(string['posture'][1]) == 0
    assert len(string['posture'][2]) == 0

    assert pytest.approx(string['posture'][3][0], 0.00001) == 0.08750000000000001
    assert pytest.approx(string['posture'][3][1], 0.00001) == 0.08750000000000001
    assert pytest.approx(string['posture'][3][2], 0.00001) == 0.08750000000000001
