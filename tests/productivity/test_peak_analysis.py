"""Tests the peak analysis implementation.

@ author Jessie Zhang
Copyright Iterate Labs, Inc. 2018-
"""
import os
import unittest

from ergo_analytics import LoadDataFromLocalDisk
from productivity import peak_analysis
from productivity.peak_analysis import PeakAnalyzer
import pandas as pd

ROOT_DIR = os.path.abspath(os.path.expanduser("."))


class TestPeakAnalysis(unittest.TestCase):
    def test_none_data(self):
        test_data = None
        peak_analyzer = PeakAnalyzer(test_data)
        report = peak_analyzer.generate_peak_report()

        parameter_names = peak_analyzer._peak_parameters_dic.keys()

        self.assertTrue(parameter_names == report.keys())
        self.assertTrue("high_peak" in parameter_names)
