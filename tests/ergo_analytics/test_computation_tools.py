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
        scores = np.linspace(0, 1, 10, endpoint=True)
        get_weighted_average = computation_tools.get_weighted_average
        weighted_average = get_weighted_average(
            scores, bins=4, bin_weights=(2, 3, 4, 5)
        )
        self.assertTrue(weighted_average == np.mean(scores))

    def test_scores_case_1(self):
        scores = np.linspace(0, 7, 14, endpoint=True)
        get_weighted_average = computation_tools.get_weighted_average
        weighted_average = get_weighted_average(
            scores, bins=4, bin_weights=(2, 3, 4, 5)
        )
        self.assertTrue(weighted_average > np.mean(scores))
        self.assertTrue(weighted_average < np.max(scores))

    def test_scores_case_2(self):
        scores = np.linspace(4, 7, 14, endpoint=True)
        get_weighted_average = computation_tools.get_weighted_average
        weighted_average = get_weighted_average(
            scores, bins=4, bin_weights=(2, 3, 4, 5)
        )
        self.assertTrue(weighted_average > np.mean(scores))
        self.assertTrue(weighted_average < np.max(scores))

    def test_scores_case_scale_to_middle(self):
        """
        scores range high. weighted to middle with bin_weights=(1,2,1).
        weighted average will be lower than mean.
        """
        scores = np.linspace(4, 7, 14, endpoint=True)
        get_weighted_average = computation_tools.get_weighted_average
        weighted_average = get_weighted_average(scores, bins=3, bin_weights=(1, 2, 1))
        self.assertTrue(weighted_average < np.mean(scores))
        self.assertTrue(weighted_average < np.max(scores))

    def test_scores_case_scale_down(self):
        """
        weighted to left (low) with bin_weights = (5,4,3,2).
        weighted average will be lower than mean.
        """
        scores = [0.5 * i for i in range(14)]
        get_weighted_average = computation_tools.get_weighted_average
        weighted_average = get_weighted_average(
            scores, bins=4, bin_weights=(5, 4, 3, 2)
        )
        self.assertTrue(weighted_average < np.mean(scores))
        self.assertTrue(weighted_average < np.max(scores))
