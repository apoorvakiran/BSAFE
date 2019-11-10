# -*- coding: utf-8 -*-
"""
Computes the posture score among the Iterate Labs Ergo Metrics.

@ author Jacob Tyrrell and Jesper Kristensen
Copyright Iterate Labs 2018-
"""

__all__ = ["compute_posture_score"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import numpy as np
from numpy import absolute
from ergo_analytics.metrics import compute_binned_score
from ergo_analytics.metrics import normalize_to_scale


def compute_posture_score(delta_pitch=None, delta_yaw=None,
                          delta_roll=None, safe_threshold=None,
                          final_scale=(0, 7)):
    """
    Takes values of yaw, pitch, and roll, and calculates posture score
    as percent of time spent outside of a "safe" posture degree value.
    """
    # This score is inherently on a scale of 0-1 so does not need
    # datasets to calibrate - however, if we want to turn this into
    # a weighted score (which is very possible) then we would need them

    # Whenever any of the delta angles extend beyond the safe region,
    # count that as an unsafe event:

    delta_yaw = absolute(delta_yaw)
    delta_pitch = absolute(delta_pitch)
    delta_roll = absolute(delta_roll)

    if np.any(delta_yaw) > 180:
        raise Exception("Delta Yaw values outside range [-180, 180]")
    if np.any(delta_pitch) > 180:
        raise Exception("Delta Pitch values outside range [-180, 180]")
    if np.any(delta_roll) > 180:
        raise Exception("Delta Roll values outside range [-180, 180]")

    num_unsafe = len(np.where((absolute(delta_pitch) > safe_threshold) | 
                              (absolute(delta_yaw) > safe_threshold) | 
                              (absolute(delta_roll) > safe_threshold))[0])
    num_total = len(delta_yaw)

    bins = [safe_threshold, 180]
    score_yaw_raw = compute_binned_score(bins=bins, values=delta_yaw,
                                         weighing_method='linear')
    score_pitch_raw = compute_binned_score(bins=bins, values=delta_pitch,
                                           weighing_method='linear')
    score_roll_raw = compute_binned_score(bins=bins, values=delta_roll,
                                          weighing_method='linear')

    # summarize posture scores
    posture_scores = dict(yaw_raw=score_yaw_raw,
                          pitch_raw=score_pitch_raw,
                          roll_raw=score_roll_raw,
                          unsafe_raw=num_unsafe / num_total)
    # the raw scores are in the range (0, 1)
    # now convert to (0, 7):

    posture_scores['yaw'] = normalize_to_scale(old_lo=0, old_hi=1,
                                               new_lo=final_scale[0],
                                               new_hi=final_scale[1],
                                               values=posture_scores['yaw_raw'])

    posture_scores['pitch'] = normalize_to_scale(old_lo=0, old_hi=1,
                                               new_lo=final_scale[0],
                                               new_hi=final_scale[1],
                                           values=posture_scores['pitch_raw'])

    posture_scores['roll'] = normalize_to_scale(old_lo=0, old_hi=1,
                                                 new_lo=final_scale[0],
                                                 new_hi=final_scale[1],
                                            values=posture_scores['roll_raw'])

    posture_scores['unsafe'] = normalize_to_scale(old_lo=0, old_hi=1,
                                                new_lo=final_scale[0],
                                                new_hi=final_scale[1],
                                            values=posture_scores['unsafe_raw'])

    return posture_scores
