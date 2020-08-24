# -*- coding: utf-8 -*-
"""Tests the report implementation.

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

ROOT_DIR = os.path.abspath(os.path.expanduser("."))


def test_report():

    data_format_code = "5"
    test_data_path = os.path.join(
        ROOT_DIR, "Demos", f"demo-format-{data_format_code}", "data_small.csv"
    )
    test_data = pd.read_csv(test_data_path)

    #
    pipeline = DataFilterPipeline()
    pipeline.add_filter(name="construct-delta", filter=ConstructDeltaValues())
    pipeline.add_filter(name="quadrant", filter=QuadrantFilter())

    list_of_structured_data_chunks = pipeline.run(
        on_raw_data=test_data,
        with_format_code=data_format_code,
        is_sorted=True,
        use_subsampling=True,
        subsample_size_index=8000,
        number_of_subsamples=4,
        randomize_subsampling=False,
    )

    list_of_structured_data_chunks[1] = []
    list_of_structured_data_chunks[2] = None

    metrics = ErgoMetrics(list_of_structured_data_chunks=list_of_structured_data_chunks)
    metrics.add(AngularActivityScore)
    metrics.add(PostureScore)
    metrics.compute()

    reporter = ErgoReport(ergo_metrics=metrics)

    string = reporter.to_string()
    assert type(string) == str


def test_http():

    data_format_code = "5"
    test_data_path = os.path.join(
        ROOT_DIR, "Demos", f"demo-format-{data_format_code}", "data_small.csv"
    )
    test_data = pd.read_csv(test_data_path)

    #
    pipeline = DataFilterPipeline()
    pipeline.add_filter(name="construct-delta", filter=ConstructDeltaValues())
    pipeline.add_filter(name="quadrant", filter=QuadrantFilter())

    list_of_structured_data_chunks = pipeline.run(
        on_raw_data=test_data,
        with_format_code=data_format_code,
        is_sorted=True,
        use_subsampling=True,
        subsample_size_index=8000,
        number_of_subsamples=4,
        randomize_subsampling=False,
    )

    metrics = ErgoMetrics(list_of_structured_data_chunks=list_of_structured_data_chunks)
    metrics.add(AngularActivityScore)
    metrics.add(PostureScore)
    metrics.compute()

    reporter = ErgoReport(ergo_metrics=metrics)

    # test that we are sending the correct format:
    payload = reporter.to_http(just_return_payload=True)

    # here we check that the payload is OK:
    # make sure all keys are as expected:
    assert "speed_yaw_score" in payload
    assert "speed_pitch_score" in payload
    assert "speed_roll_score" in payload
    assert "speed_score" in payload
    #
    assert "posture_yaw_score" in payload
    assert "posture_pitch_score" in payload
    assert "posture_roll_score" in payload
    assert "posture_score" in payload
    #
    assert "strain_yaw_score" in payload
    assert "strain_pitch_score" in payload
    assert "strain_roll_score" in payload
    assert "strain_score" in payload
    #
    assert "safety_score" in payload
    #
    assert "recommendation_id" in payload
    assert "safety_score_average" in payload
    assert "safety_score_vs_time" in payload
    assert "weighted_safety_score_average" in payload
    #
    assert "start_time" in payload
    assert "end_time" in payload
