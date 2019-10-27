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


def compute_strain_score(delta_pitch=None, delta_yaw=None, delta_roll=None,
                         normalize_to_scale=(0, 7), weighing_method='linear'):
    """
    Given the yaw pitch and roll in their delta format, compute the associated
    strain score.

    Assumption:
        The incoming data is in degrees.
    """

    m = 11  # how many bins?
    bins_degrees = [15 * (i + 1) for i in range(m + 1)]
    # bins are: [0, 15, 30, 45, ...]

    # but we also need to weigh by how much time is spent at this value
    # that contributed to the bin. For example:
    # [0,0,0,0,0,0,0,0,....,0,0,0,0,178] should be a low score even though
    # 178 is hit, it's for such a short time compared to the total time which
    # is spent at 0 deg!

    # now count each (yaw/pitch/roll) degree in the given degree bins
    # for example - if yaw had a value of 4 at one time instance that
    # value would end up in the first bin which covers "0-15". Note that we
    # don't care about the direction so we take the absolute values and
    # then we bin them.

    delta_yaw_abs = np.abs(delta_yaw)
    delta_pitch_abs = np.abs(delta_pitch)
    delta_roll_abs = np.abs(delta_roll)

    try:
        pitch_bins = digitize_values(values=delta_pitch_abs, bins=bins_degrees)
        yaw_bins = digitize_values(values=delta_yaw_abs, bins=bins_degrees)
        roll_bins = digitize_values(values=delta_roll_abs, bins=bins_degrees)
    except IndexError:
        # we could also do a np.clip(...) based on the known bins above
        msg = "The values seem to be outside the range [-180, 180].\n"
        msg += "Consider applying a centering filter and/or others."
        logger.exception(msg)
        raise Exception(msg)

    # the following sum is a way to take the bins and condense into a single
    # metric representing the scores:
    raw_score_yaw = _custom_weighted_sum(list_of_bins=yaw_bins,
                                         weighing_method=weighing_method)
    raw_score_pitch = _custom_weighted_sum(list_of_bins=pitch_bins,
                                           weighing_method=weighing_method)
    raw_score_roll = _custom_weighted_sum(list_of_bins=roll_bins,
                                          weighing_method=weighing_method)

    # scores coming out are always [0, m] where "m" is number of bins used

    # now normalize to incoming scale (say the incoming is (2, 10)
    # for an example):
    raw_score_yaw /= m  # bring to (0, 1)
    raw_score_yaw *= (normalize_to_scale[1] - normalize_to_scale[0])  # (0, 8)
    raw_score_yaw += normalize_to_scale[0]  # (2, 10)
    #
    raw_score_pitch /= m  # bring to (0, 1)
    raw_score_pitch *= (normalize_to_scale[1] - normalize_to_scale[0])  # (0, 8)
    raw_score_pitch += normalize_to_scale[0]  # (2, 10)
    #
    raw_score_roll /= m  # bring to (0, 1)
    raw_score_roll *= (normalize_to_scale[1] - normalize_to_scale[0])  # (0, 8)
    raw_score_roll += normalize_to_scale[0]  # (2, 10)

    # summarize strain scores
    strain_scores = dict(yaw_raw=raw_score_yaw, pitch_raw=raw_score_pitch,
                         roll_raw=raw_score_roll)

    strain_scores['yaw'] = strain_scores['yaw_raw']
    strain_scores['pitch'] = strain_scores['pitch_raw']
    strain_scores['roll'] = strain_scores['roll_raw']

    # how to construct the total score?
    # we can take an average:
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
    list_of_bins = np.asarray(list_of_bins)  # say m = len(list_of_bins)
    counts_all_bins = sum(list_of_bins)
    # convert to fraction of time spent in each bin:
    weights_fraction_time = list_of_bins / counts_all_bins
    # these are the weights "40% in bin 2" means:
    # "weigh bin 2 by 40%" ==> "bin 2's value" * 40%
    # so note that the counts in the bins are not the "bin2 value"
    # they are the weights. But we are free to modify the bin values
    # with whatever we want and that is where "weighing_method" comes in.

    weighted_score = 0
    total_weight = 0
    for bin_ix in range(len(weights_fraction_time)):  # [0, 1, 2, ..., m]
        # written in a general way to support custom weighing functions:
        # pick this bin out of the list:

        weight_fraction_this_bin = weights_fraction_time[bin_ix]

        # now we apply a weight-modifier on top of the pure "fraction weight":
        if weighing_method == 'constant':
            # only apply weights to bins not the first one:
            weight_custom = 1.
        elif weighing_method == 'linear':
            weight_custom = (bin_ix + 1)
        elif weighing_method == 'quadratic':
            weight_custom = (bin_ix + 1) ** 2
        else:
            raise Exception(f"Weighing function '{weighing_method}' "
                            f"not implemented!")

        combined_weight = weight_fraction_this_bin * weight_custom
        this_score = bin_ix  # better name for increased understanding below
        sum_contribution = this_score * combined_weight

        total_weight += combined_weight
        weighted_score += sum_contribution

    effective_score = weighted_score
    if total_weight > 0:
        effective_score /= total_weight

    # the score is now in a range [0, m]

    return effective_score
