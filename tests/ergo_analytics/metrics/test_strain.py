# -*- coding: utf-8 -*-
"""
Tests the implementation of the strain score.

@ author Jesper Kristensen
Copyright Iterate Labs, Inc. 2018-
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import pytest
from unittest.mock import MagicMock
from ergo_analytics.metrics import _custom_weighted_sum


def test_strain_constant_weights():
    """
    Run a test to confirm that the strain score makes sense.
    """

    # # lowest case: all time spent in 0-15 degrees
    # list_of_bins = [400, 0, 0, 0, 0]
    # score = _custom_weighted_sum(list_of_bins=list_of_bins,
    #                              weighing_method='constant')
    # # with constant weighing method, we assign equal weight of 1/num_bins
    # # to each bin - so score is 1/num_bins = 1/5 = 0.2:
    # assert score == 0.2

    # # highest case:
    # list_of_bins = [0, 0, 0, 0, 400]
    # score = _custom_weighted_sum(list_of_bins=list_of_bins,
    #                              weighing_method='constant')
    # assert score == 0.2  # same score as above, since we are not ramping up
    # # assigning more score to higher values

    list_of_bins = [0.2, 0.2, 0.2, 0.2, 0.2]
    score = _custom_weighted_sum(list_of_bins=list_of_bins,
                                 weighing_method='quadratic')
    # assert score == 0.2

    import pdb
    pdb.set_trace()

    # em = ErgoMetrics(structured_data=data)
    # em.compute()

    # assert pytest.approx(em.get_score(name='total'), 0.0001) == 0.338715
