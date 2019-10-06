# -*- coding: utf-8 -*-
"""
Computes the motion score among the Iterate Labs Ergo Metrics.

@ author Jacob Tyrrell and Jesper Kristensen
Copyright Iterate Labs 2018-
"""

__all__ = ["compute_motion_score"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import numpy as np
from ErgoAnalytics.utilities import digitize_values


def compute_motion_score(delta_pitch=None, delta_yaw=None, delta_roll=None, safe=None):
    """
    Pass lists of Yaw, Pitch, Roll, returns yaw, pitch, roll, and
    total motion scores.
    """

    bins_degrees = [15 * i for i in range(10 + 1)]  # [0, 15, 30, 45, 60, 75,
    # 90, 105, 120, 135, 150]
    
    # now count each (yaw/pitch/roll) degree in the given degree bins
    # for example - if yaw had a value of 4 at one time instance that
    # value would end up in bin 1 and so forth:
    pitch_bins = digitize_values(values=np.abs(delta_pitch), bins=bins_degrees)
    yaw_bins = digitize_values(values=np.abs(delta_yaw), bins=bins_degrees)
    roll_bins = digitize_values(values=np.abs(delta_roll), bins=bins_degrees)
    
    raw_score_yaw = custom_weighted_sum(yaw_bins)
    raw_score_pitch = custom_weighted_sum(pitch_bins)
    raw_score_roll = custom_weighted_sum(roll_bins)
    
    adjuster = 1200 / len(bins_degrees)

    score_yaw = raw_score_yaw * adjuster
    score_pitch = raw_score_pitch * adjuster
    score_roll = raw_score_roll * adjuster

    # for the total score:
    score_total = score_yaw + score_pitch + score_roll
    score_total = score_total / 2214

    return score_pitch, score_yaw, score_roll, score_total


def custom_weighted_sum(list_of_bins=None, weighing_method="linear"):
    """
    Applies a custom weighing function to a list of bins.

    So if the list is:
    list_of_bins = [1,1,4,8,1] as an example and weighing is linear, we compute:

    weighted_sum = 1 * (0) + 1 * (1) + 4 * (2) + 8 * (3) + 1 * (4)
    where the number in each parenthesis represents the weight applied.
    Here it's linear since it increases linearly with bin number.
    """
    weighted_total = 0
    for bin_ix in range(len(list_of_bins)):
        # written in a general way to support custom weighing functions:
        counts_in_this_bin = list_of_bins[bin_ix]  # pick this bin out of the list

        if weighing_method == 'linear':
            weight = bin_ix  # set the weight to the bin index - notice it can be 0
            sum_contribution = counts_in_this_bin * weight
        else:
            raise Exception("Weighing function '{}' not implemented!".format(weighing_method))
        
        weighted_total += sum_contribution
        
    return weighted_total
