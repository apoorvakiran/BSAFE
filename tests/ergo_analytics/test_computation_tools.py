"""Tests computation tools.

@ author Jessie Zhang
Copyright Iterate Labs, Inc. 2018-
"""
import unittest
import numpy as np
from ergo_analytics import computation_tools


class TestActiveScore(unittest.TestCase):
    def test_empty_scores(self):
        scores = []
        get_weighted_average = computation_tools.get_weighted_average
        weighted_average = get_weighted_average(scores)
        self.assertTrue(weighted_average == 0)

    def test_one_scores(self):
        scores = [1]
        get_weighted_average = computation_tools.get_weighted_average
        weighted_average = get_weighted_average(scores)
        self.assertTrue(weighted_average == scores[0])

    def test_scores_in_same_bin(self):
        """
        If all scores in same bin, the weighted average score should be equal to np.mean
        """
        scores = [3.6, 3.7, 3.8, 3.9, 4.3]
        get_weighted_average = computation_tools.get_weighted_average
        weighted_average = get_weighted_average(
            scores, bins=4, bin_weights=(2, 3, 4, 5)
        )
        self.assertTrue(weighted_average == np.mean(scores))

    def test_scores_case_1(self):
        scores = [3.5 + 0.25 * i for i in range(14)]
        get_weighted_average = computation_tools.get_weighted_average
        weighted_average = get_weighted_average(
            scores, bins=4, bin_weights=(2, 3, 4, 5)
        )
        self.assertTrue(weighted_average > np.mean(scores))
        self.assertTrue(weighted_average < np.max(scores))

    def test_scores_case_2(self):
        scores = [0.25 * i for i in range(14)]
        get_weighted_average = computation_tools.get_weighted_average
        weighted_average = get_weighted_average(
            scores, bins=4, bin_weights=(2, 3, 4, 5)
        )
        self.assertTrue(weighted_average > np.mean(scores))
        self.assertTrue(weighted_average < np.max(scores))

    def test_scores_case_3(self):
        scores = [0.5 * i for i in range(14)]
        get_weighted_average = computation_tools.get_weighted_average
        weighted_average = get_weighted_average(
            scores, bins=4, bin_weights=(2, 3, 4, 5)
        )
        self.assertTrue(weighted_average > np.mean(scores))
        self.assertTrue(weighted_average < np.max(scores))
