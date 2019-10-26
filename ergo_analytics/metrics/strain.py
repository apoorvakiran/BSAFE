# -*- coding: utf-8 -*-
"""
Computes the motion score among the Iterate Labs Ergo Metrics.

@ author Jacob Tyrrell and Jesper Kristensen
Copyright Iterate Labs 2018-
"""

__all__ = ["compute_strain_score", "_custom_weighted_sum"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import numpy as np
from ergo_analytics.utilities import digitize_values
import logging

logger = logging.getLogger()


def compute_strain_score(delta_pitch=None, delta_yaw=None, delta_roll=None):
    """
    Given the yaw pitch and roll in their delta format, compute the associated
    strain score.

    Assumption:
        The incoming data is in degrees.
    """

    bins_degrees = [15 * (i + 1) for i in range(11 + 1)]
    # bins are: [0, 15, 30, 45, ...]

    # now count each (yaw/pitch/roll) degree in the given degree bins
    # for example - if yaw had a value of 4 at one time instance that
    # value would end up in the first bin which covers "0-15". Note that we
    # don't care about the direction so we take the absolute values and
    # then we bin them.

    try:
        pitch_bins = digitize_values(values=np.abs(delta_pitch),
                                     bins=bins_degrees)
        yaw_bins = digitize_values(values=np.abs(delta_yaw), bins=bins_degrees)
        roll_bins = digitize_values(values=np.abs(delta_roll),
                                    bins=bins_degrees)
    except IndexError:
        msg = "The values seem to be outside the range [-180, 180].\n"
        msg += "Consider applying a centering filter and/or others."
        logger.exception(msg)
        raise Exception(msg)

    # the following sum is a way to take the bins and condense into a single
    # metric representing the scores:
    raw_score_yaw = _custom_weighted_sum(yaw_bins)
    raw_score_pitch = _custom_weighted_sum(pitch_bins)
    raw_score_roll = _custom_weighted_sum(roll_bins)

    # summarize strain scores
    strain_scores = dict(yaw_raw=raw_score_yaw, pitch_raw=raw_score_pitch,
                         roll_raw=raw_score_roll)

    # TODO(JTK): need a reasonable adjuster here:
    # this is one of the reasons we need the representative datasets
    adjuster = 1

    strain_scores['yaw'] = strain_scores['yaw_raw'] * adjuster
    strain_scores['pitch'] = strain_scores['pitch_raw'] * adjuster
    strain_scores['roll'] = strain_scores['roll_raw'] * adjuster
    strain_scores['total'] = (strain_scores['yaw'] + strain_scores['pitch']
                              + strain_scores['roll']) / 3

    return strain_scores


def _custom_weighted_sum(list_of_bins=None, weighing_method="linear"):
    """
    Applies a custom weighing function to a list of bins.

    So if the list is:
    list_of_bins = [1,1,4,8,1] as an example and weighing is linear, we compute:

    weighted_sum = 1 * (0) + 1 * (1) + 4 * (2) + 8 * (3) + 1 * (4)
    where the number in each parenthesis represents the weight applied.
    Here it's linear since it increases linearly with bin number.
    """

    list_of_bins = np.asarray(list_of_bins)

    num_bins = len(list_of_bins)
    counts_all_bins = sum(list_of_bins)

    # convert to fraction of time spent in each bin:
    weights = list_of_bins / counts_all_bins
    # these are the weights "40% in bin 2" means:
    # "weigh bin 2 by 40%" ==> "bin 2's value" * 40%
    # so note that the counts in the bins are not the "bin2 value"
    # they are the weights. But we are free to modify the bin values
    # with whatever we want and that is where "weighing_method" comes in.

    assert 0.99 < sum(weights) < 1.01

    weighted_total = 0
    total_bin_values = 0
    for bin_ix in range(len(weights)):
        # written in a general way to support custom weighing functions:
        # pick this bin out of the list:
        weight_this_bin = weights[bin_ix]

        if weighing_method == 'constant':
            # only apply weights to bins not the first one:
            bin_value = 1.
        elif weighing_method == 'linear':
            bin_value = bin_ix  # set the bin_value to the bin index
            # (linear ramp) - notice it can be 0
        elif weighing_method == 'quadratic':
            bin_value = bin_ix ** 2
        else:
            raise Exception(f"Weighing function '{weighing_method}' "
                            f"not implemented!")

        sum_contribution = bin_value * weight_this_bin

        total_bin_values += bin_value
        weighted_total += sum_contribution

    # divide by largest possible bin value
    weighted_total /= bin_value

    return weighted_total
