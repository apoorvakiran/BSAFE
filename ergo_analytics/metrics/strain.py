# -*- coding: utf-8 -*-
"""
Computes the motion score among the Iterate Labs Ergo Metrics.

@ author Jacob Tyrrell and Jesper Kristensen
Copyright Iterate Labs 2018-
"""

__all__ = ["compute_strain_score"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import numpy as np
from ergo_analytics.utilities import digitize_values
import logging

logger = logging.getLogger()


def compute_strain_score(delta_pitch=None, delta_yaw=None,
                         delta_roll=None):
    """
    Pass lists of Yaw, Pitch, Roll, returns yaw, pitch, roll, and
    total motion scores.
    """

    bins_degrees = [15 * i for i in range(12 + 1)]  # [0, 15, 30, 45, 60, 75,
    # 90, 105, 120, 135, 150, 165, 180]

    # now count each (yaw/pitch/roll) degree in the given degree bins
    # for example - if yaw had a value of 4 at one time instance that
    # value would end up in bin 1 and so forth:

    try:
        pitch_bins = digitize_values(values=np.abs(delta_pitch), bins=bins_degrees)
        yaw_bins = digitize_values(values=np.abs(delta_yaw), bins=bins_degrees)
        roll_bins = digitize_values(values=np.abs(delta_roll), bins=bins_degrees)
    except IndexError:
        msg = "The values seem to be outside the range [-180, 180].\n"
        msg += "Consider applying a centering filter and/or others."
        logger.exception(msg)
        raise Exception(msg)
    
    raw_score_yaw = custom_weighted_sum(yaw_bins)
    raw_score_pitch = custom_weighted_sum(pitch_bins)
    raw_score_roll = custom_weighted_sum(roll_bins)

    # summarize strain scores
    strain_scores = dict(yaw_raw=raw_score_yaw,
                          pitch_raw=raw_score_pitch,
                          roll_raw=raw_score_roll)

    adjuster = 1200 / len(bins_degrees)

    strain_scores['yaw'] = strain_scores['yaw_raw'] * adjuster
    strain_scores['pitch'] = strain_scores['pitch_raw'] * adjuster
    strain_scores['roll'] = strain_scores['roll_raw'] * adjuster
    strain_scores['total'] = (strain_scores['yaw'] + strain_scores['pitch']
                              + strain_scores['roll']) / 2214

    return strain_scores


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
        # pick this bin out of the list:
        counts_in_this_bin = list_of_bins[bin_ix]

        if weighing_method == 'linear':
            weight = bin_ix  # set the weight to the bin index
            # ^^ notice it can be 0
            sum_contribution = counts_in_this_bin * weight
        else:
            raise Exception(f"Weighing function '{weighing_method}' "
                            f"not implemented!")
        
        weighted_total += sum_contribution
        
    return weighted_total
