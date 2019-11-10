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
from ergo_analytics import ErgoMetrics
from ergo_analytics.metrics import custom_weighted_sum


def test_strain_constant_weights():
    """
    Run a test to confirm that the strain score makes sense.
    """

    # lowest case: all time spent in 0-15 degrees
    list_of_bins = [400, 0, 0, 0, 0]
    score = custom_weighted_sum(list_of_bins=list_of_bins,
                                 weighing_method='constant')
    # we have 400 counts in bin with weight "0"
    # since the counts are not spread out over multiple bins
    # here it just means "you are 100% in the first bin - and that has a value of 0":
    assert score == 0.0

    # highest case:
    list_of_bins = [0, 0, 0, 0, 400]
    score = custom_weighted_sum(list_of_bins=list_of_bins,
                                 weighing_method='constant')
    # here it just means "you are 100% in the last bin - and that has a value of 4":
    # (why 4? Because the bins always have values: (0, 1, 2, 3, 4))
    assert score == 4

    list_of_bins = [200, 200, 200, 200, 200]
    score = custom_weighted_sum(list_of_bins=list_of_bins,
                                 weighing_method='constant')
    # now we are spending time across all bins! So now we
    # we should get a score right in the middle of (0, 1, 2, 3, 4)
    # which is 2:
    assert score == 2

    list_of_bins = [200, 200, 200, 200, 200]
    score = custom_weighted_sum(list_of_bins=list_of_bins,
                                 weighing_method='linear')
    # same as above but now we use linear weighhing! So later bins
    # get more weight. This should slightly increase the score:
    assert score == pytest.approx(2.66, 0.01)  # so not "2" but "2.66"

    # let's try to weigh the upper bins even more than the lower bins.
    # We can do that with a quadratic weghing function (bin index) ^ 2 gets
    # larger for larger values of bin index:
    list_of_bins = [200, 200, 200, 200, 200]
    score = custom_weighted_sum(list_of_bins=list_of_bins,
                                 weighing_method='quadratic')
    # same as above but now we use linear weighhing! So later bins
    # get more weight. This should slightly increase the score:
    assert score == pytest.approx(3.0909, 0.001)
