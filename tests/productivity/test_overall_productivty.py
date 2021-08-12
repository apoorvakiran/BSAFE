"""Tests overall productivity metrics:

@ author Jessie Zhang
Copyright Iterate Labs, Inc. 2018-
"""
import os
import unittest

from ergo_analytics.metrics import AngularActivityScore, PostureScore
from productivity import active_score
import pandas as pd
from ergo_analytics import (
    LoadDataFromLocalDisk,
    DataFilterPipeline,
    ErgoMetrics,
    ErgoReport,
)
from ergo_analytics.filters import ConstructDeltaValues, QuadrantFilter
from productivity.active_score import ActiveScore

ROOT_DIR = os.path.abspath(os.path.expanduser("."))


class TestProductivity(unittest.TestCase):
    def test_productivity_on_none_input(self):
        data_format_code = "5"
        test_data_path = os.path.join(
            ROOT_DIR, "Demos", f"demo-format-{data_format_code}", "prod_data.csv"
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

        metrics = ErgoMetrics(
            list_of_structured_data_chunks=list_of_structured_data_chunks,
        )

        metrics.add(AngularActivityScore)
        metrics.add(PostureScore)
        metrics.compute()

        reporter = ErgoReport(ergo_metrics=metrics)

        # test that we are sending the correct format:
        payload = reporter.to_http(just_return_payload=True)

        self.assertTrue(type(payload) == dict)
        self.assertTrue("intense_active_score" in payload)
        self.assertTrue("mild_active_score" in payload)
        #
        self.assertTrue("high_peaks" in payload)
        self.assertTrue("medium_peaks" in payload)
        self.assertTrue("low_peaks" in payload)

    def test_productivity_on_one_row(self):
        data_format_code = "5"
        test_data_path = os.path.join(
            ROOT_DIR, "Demos", f"demo-format-{data_format_code}", "one_row_data.csv"
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

        delta_only_pipeline = DataFilterPipeline(verify_pipeline=False)
        delta_only_pipeline.add_filter(
            name="construct-delta", filter=ConstructDeltaValues()
        )
        structured_all_data = delta_only_pipeline.run(
            on_raw_data=test_data,
            with_format_code=data_format_code,
            use_subsampling=False,
        )[0].data_matrix

        assert len(test_data) == len(structured_all_data)
        assert "DeltaPitch" in structured_all_data.columns
        assert "DeltaRoll" in structured_all_data.columns
        assert "DeltaYaw" in structured_all_data.columns

        metrics = ErgoMetrics(
            list_of_structured_data_chunks=list_of_structured_data_chunks,
            structured_all_data=structured_all_data,
        )

        metrics.add(AngularActivityScore)
        metrics.add(PostureScore)
        metrics.compute()

        reporter = ErgoReport(ergo_metrics=metrics)

        # test that we are sending the correct format:
        payload = reporter.to_http(just_return_payload=True)

        self.assertTrue(type(payload) == dict)
        self.assertTrue("intense_active_score" in payload)
        self.assertTrue("mild_active_score" in payload)
        #
        self.assertTrue("high_peaks" in payload)
        self.assertTrue("medium_peaks" in payload)
        self.assertTrue("low_peaks" in payload)
        #
        self.assertEqual(payload["high_peaks"], 0)
        self.assertEqual(payload["medium_peaks"], 0)
        self.assertEqual(payload["low_peaks"], 0)
        self.assertEqual(payload["intense_active_score"], 0)
        self.assertEqual(payload["mild_active_score"], 0)

    def test_productivity_on_medium_size_data(self):
        data_format_code = "5"
        test_data_path = os.path.join(
            ROOT_DIR, "Demos", f"demo-format-{data_format_code}", "prod_data.csv"
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

        delta_only_pipeline = DataFilterPipeline(verify_pipeline=False)
        delta_only_pipeline.add_filter(
            name="construct-delta", filter=ConstructDeltaValues()
        )
        structured_all_data = delta_only_pipeline.run(
            on_raw_data=test_data,
            with_format_code=data_format_code,
            use_subsampling=False,
        )[0].data_matrix

        assert len(test_data) == len(structured_all_data)
        assert "DeltaPitch" in structured_all_data.columns
        assert "DeltaRoll" in structured_all_data.columns
        assert "DeltaYaw" in structured_all_data.columns

        metrics = ErgoMetrics(
            list_of_structured_data_chunks=list_of_structured_data_chunks,
            structured_all_data=structured_all_data,
        )

        metrics.add(AngularActivityScore)
        metrics.add(PostureScore)
        metrics.compute()

        reporter = ErgoReport(ergo_metrics=metrics)

        # test that we are sending the correct format:
        payload = reporter.to_http(just_return_payload=True)

        self.assertTrue(type(payload) == dict)
        self.assertTrue("intense_active_score" in payload)
        self.assertTrue("mild_active_score" in payload)
        #
        self.assertTrue("high_peaks" in payload)
        self.assertTrue("medium_peaks" in payload)
        self.assertTrue("low_peaks" in payload)
        #
        assert 1 > payload["mild_active_score"] > payload["intense_active_score"] > 0
        assert type(payload["high_peaks"]) == int
        assert payload["low_peaks"] > payload["high_peaks"] > 0
