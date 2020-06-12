# -*- coding: utf-8 -*-
"""Contains functionality commonly useful for all metrics.

@ author Jesper Kristensen
Copyright 2018-
All Rights Reserved
"""

import numpy as np
import logging
from ergo_analytics.utilities import digitize_values

__all__ = ["compute_binned_score", "custom_weighted_sum", "normalize_to_scale"]
__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

logger = logging.getLogger()


def compute_binned_score(bins=None, values=None, weighing_method="linear"):
    """Computes the binned score given the bins and the values to populate
    the bins with."""

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

    values_absolute = np.abs(values)

    try:
        bins_filled = digitize_values(values=values_absolute, bins=bins)
    except IndexError:
        # we could also do a np.clip(...) based on the known bins above
        msg = "The values seem to be outside the range of the bins!\n"
        msg += f"The bins range from {bins[0]} to {bins[-1]}.\n"
        msg += f"But the data ranges from {values_absolute[0]} to {values_absolute[-1]}.\n"
        msg += "Consider maybe applying a centering filter and/or others?"
        logger.exception(msg)
        raise Exception(msg)

    # import matplotlib.pyplot as plt
    # plt.plot(bins)
    # plt.show()

    # the following sum is a way to take the bins and condense into a single
    # metric representing the scores:
    raw_score_yaw = custom_weighted_sum(list_of_bins=bins_filled, weighing_method=weighing_method)

    return raw_score_yaw


def custom_weighted_sum(list_of_bins=None, weighing_method="linear"):
    """Applies a custom weighing function to a list of bins.

    So if the list is:
    list_of_bins = [1,1,4,8,1] as an example and weighing is linear, we compute:

    weighted_sum = 1 * (0) + 1 * (1) + 4 * (2) + 8 * (3) + 1 * (4)
    where the number in each parenthesis represents the weight applied.
    Here it's linear since it increases linearly with bin number.

    We can also weigh constantly or quadratically, etc.
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
        if weighing_method == "constant":
            # only apply weights to bins not the first one:
            weight_custom = 1.0
        elif weighing_method == "linear":
            weight_custom = bin_ix + 1
        elif weighing_method == "quadratic":
            weight_custom = (bin_ix + 1) ** 2
        else:
            raise Exception(f"Weighing function '{weighing_method}' " f"not implemented!")

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


def normalize_to_scale(values=None, old_lo=None, old_hi=None, new_lo=None, new_hi=None):
    """Converts a set of values from an old scale in range [old_lo, old_hi]
    to a new scale [new_lo, new_hi].

    For example, say you have computed something on a scale from [0, 100], but
    now want to express those values on a scale from [0, 7]. This function
    does just that.

    :return values: values on the new scale.
    """

    if values is None:
        return

    values = np.atleast_1d(values)

    if len(values) == 0:
        return []

    values = values - old_lo  #
    values = values / (old_hi - old_lo)  # bring to (0, 1)

    values = values * (new_hi - new_lo)  #
    values = values + new_lo  # now in range (new_lo, new_hi)

    return values
