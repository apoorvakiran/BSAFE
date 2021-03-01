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

    def test_short_data(self):
        pass
        # test_data_path = os.path.join(
        #     ROOT_DIR, "Demos", f"demo-format-5", "data_small.csv"
        # )
        #
        # assert os.path.isfile(test_data_path)
        #
        # put_structured_data_here = os.path.join(ROOT_DIR, "tests", "system")
        #
        # raw_data_loader = LoadDataFromLocalDisk()
        # raw_data = raw_data_loader.get_data(
        #     path=test_data_path, destination=put_structured_data_here,
        # )
        # file_path = "Demos/demo-format-5/data_small.csv"
        # test_data = pd.read_csv(file_path)
        # peak_analyzer = PeakAnalyzer(test_data)
        # report = peak_analyzer.generate_peak_report()
        # parameter_names = peak_analyzer._peak_parameters_dic.keys()
        #
        # self.assertTrue(parameter_names == report.keys())
        # self.assertTrue("high_peak" in parameter_names)
        # self.assertTrue(isinstance(report["high_peak"], int))

    def test_medium_size_data(self):
        pass
        # file_path = "Demos/demo-format-5/data.csv"
        # test_data = pd.read_csv(file_path)
        # peak_analyzer = PeakAnalyzer(test_data)
        # report = peak_analyzer.generate_peak_report()
        # parameter_names = peak_analyzer._peak_parameters_dic.keys()
        #
        # self.assertTrue(parameter_names == report.keys())
        # self.assertTrue("high_peak" in parameter_names)
        # self.assertTrue(isinstance(report["high_peak"], int))
        # self.assertTrue(isinstance(report["medium_peak"], int))
        # self.assertTrue(isinstance(report["low_peak"], int))
        # self.assertTrue(report["low_peak"] >= report["high_peak"])
