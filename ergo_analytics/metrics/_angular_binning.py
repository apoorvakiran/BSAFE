# -*- coding: utf-8 -*-
"""Computes the motion score among the Iterate Labs Ergo Metrics.

@ author Jesper Kristensen
Copyright Iterate Labs 2018-
"""

__all__ = ["angular_binning"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import numpy as np

from ergo_analytics.metrics import compute_binned_score
from ergo_analytics.metrics import normalize_to_scale
import logging

logger = logging.getLogger()


def angular_binning(
    delta_pitch=None,
    delta_yaw=None,
    delta_roll=None,
    final_scale=(0, 7),
    weighing_method="linear",
    total_score_method="max",
    number_of_bins=3,
    exclude_angles=None,
):
    """
    Given the yaw pitch and roll in their delta format, compute the associated
    strain score.

    Assumption:
        The incoming data is in degrees.
    """

    if delta_pitch is None or delta_yaw is None or delta_roll is None:
        msg = "one or more of the incoming delta-angles is None!" "Returning just None for the score."
        logger.debug(msg)
        return None

    if exclude_angles is None:
        exclude_angles = ()

    m = number_of_bins  # how many bins?
    bins_degrees = [15 * (i + 1) for i in range(m + 1)]
    # bins are: [0, 15, 30, 45, ...]

    total_count = 0
    if "yaw" not in exclude_angles:
        raw_score_yaw = compute_binned_score(bins=bins_degrees, values=delta_yaw, weighing_method=weighing_method)
        total_count += 1
    else:
        raw_score_yaw = 0

    if "pitch" not in exclude_angles:
        raw_score_pitch = compute_binned_score(bins=bins_degrees, values=delta_pitch, weighing_method=weighing_method)
        total_count += 1
    else:
        raw_score_pitch = 0

    if "roll" not in exclude_angles:
        raw_score_roll = compute_binned_score(bins=bins_degrees, values=delta_roll, weighing_method=weighing_method)
        total_count += 1
    else:
        raw_score_roll = 0

    # scores coming out are always on the scale [0, m] where "m" is
    # number of bins used

    # now normalize to incoming scale:
    raw_score_yaw = normalize_to_scale(
        old_lo=0, old_hi=m, new_lo=final_scale[0], new_hi=final_scale[1], values=raw_score_yaw
    )

    raw_score_pitch = normalize_to_scale(
        old_lo=0, old_hi=m, new_lo=final_scale[0], new_hi=final_scale[1], values=raw_score_pitch
    )

    raw_score_roll = normalize_to_scale(
        old_lo=0, old_hi=m, new_lo=final_scale[0], new_hi=final_scale[1], values=raw_score_roll
    )

    # summarize strain scores
    strain_scores = dict(yaw_raw=raw_score_yaw, pitch_raw=raw_score_pitch, roll_raw=raw_score_roll)

    strain_scores["yaw"] = strain_scores["yaw_raw"]
    strain_scores["pitch"] = strain_scores["pitch_raw"]
    strain_scores["roll"] = strain_scores["roll_raw"]

    # how to construct the total score?
    if total_score_method == "average":
        # we can take an average:
        strain_scores["total"] = (strain_scores["yaw"] + strain_scores["pitch"] + strain_scores["roll"]) / total_count
    elif total_score_method == "max":
        # or the max:
        strain_scores["total"] = np.max([np.max([strain_scores["yaw"], strain_scores["pitch"]]), strain_scores["roll"]])
    else:
        raise NotImplementedError("Implement me!")

    return strain_scores
