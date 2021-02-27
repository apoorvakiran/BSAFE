"""Tests the peak analysis implementation.

@ author Jessie Zhang
Copyright Iterate Labs, Inc. 2018-
"""
import unittest
from productivity import peak_analysis
from productivity.peak_analysis import PeakAnalyzer
import pandas as pd


class TestPeakAnalysis(unittest.TestCase):
    def test_none_data(self):
        test_data = None
        peak_analyzer = PeakAnalyzer(test_data)
        report = peak_analyzer.generate_peak_report()

        parameter_names = peak_analyzer._peak_parameters_dic.keys()

        self.assertTrue(parameter_names == report.keys())
        self.assertTrue("high_peak" in parameter_names)

    def test_short_data(self):
        file_path = "Demos/demo-data-with-delta/small_delta_data_sample_1.csv"
        test_data = pd.read_csv(file_path)
        peak_analyzer = PeakAnalyzer(test_data)
        report = peak_analyzer.generate_peak_report()
        parameter_names = peak_analyzer._peak_parameters_dic.keys()

        self.assertTrue(parameter_names == report.keys())
        self.assertTrue("high_peak" in parameter_names)
        self.assertTrue(isinstance(report["high_peak"], int))

    def test_medium_size_data(self):
        file_path = "Demos/demo-data-with-delta/medium_delta_data_sample_1.csv"
        test_data = pd.read_csv(file_path)
        peak_analyzer = PeakAnalyzer(test_data)
        report = peak_analyzer.generate_peak_report()
        parameter_names = peak_analyzer._peak_parameters_dic.keys()

        self.assertTrue(parameter_names == report.keys())
        self.assertTrue("high_peak" in parameter_names)
        self.assertTrue(isinstance(report["high_peak"], int))
        self.assertTrue(isinstance(report["medium_peak"], int))
        self.assertTrue(isinstance(report["low_peak"], int))
        self.assertTrue(report["low_peak"] >= report["high_peak"])
