# -*- coding: utf-8 -*-
"""Computes the posture score among the Iterate Labs Ergo Metrics.

@ author Jesper Kristensen
Copyright Iterate Labs 2018-
All Rights Reserved.
"""

__all__ = ["time_beyond_threshold"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import logging
import numpy as np
from numpy import absolute
from ergo_analytics.metrics import compute_binned_score
from ergo_analytics.metrics import normalize_to_scale

logger = logging.getLogger()


def time_beyond_threshold(delta_pitch=None, delta_yaw=None,
                          delta_roll=None, safe_threshold=None,
                          final_scale=(0, 7), exclude_angles=None):
    """Takes values of yaw, pitch, and roll, and calculates posture score.

    This is defined as percent of time spent outside of a "safe"
    posture degree value. So this is "time beyond threshold".
    """
    # This score is inherently on a scale of 0-1 so does not need
    # datasets to calibrate - however, if we want to turn this into
    # a weighted score (which is very possible) then we would need them

    # Whenever any of the delta angles extend beyond the safe region,
    # count that as an unsafe event:

    if delta_pitch is None or delta_yaw is None or delta_roll is None:
        msg = "one or more of the incoming delta-angles is None!" \
              "Returning just None for the score."
        logger.debug(msg)
        return None

    if exclude_angles is None:
        exclude_angles = ()

    delta_yaw = absolute(delta_yaw)
    delta_pitch = absolute(delta_pitch)
    delta_roll = absolute(delta_roll)

    if np.any(delta_yaw) > 180:
        raise Exception("Delta Yaw values outside range [-180, 180]")
    if np.any(delta_pitch) > 180:
        raise Exception("Delta Pitch values outside range [-180, 180]")
    if np.any(delta_roll) > 180:
        raise Exception("Delta Roll values outside range [-180, 180]")

    if 'yaw' in exclude_angles:
        delta_yaw = np.zeros(len(delta_yaw))

    if 'pitch' in exclude_angles:
        delta_pitch = np.zeros(len(delta_pitch))

    if 'roll' in exclude_angles:
        delta_pitch = np.zeros(len(delta_roll))

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

    if 'yaw' in exclude_angles:
        posture_scores['yaw'] = 0

    if 'pitch' in exclude_angles:
        posture_scores['pitch'] = 0

    if 'roll' in exclude_angles:
        posture_scores['roll'] = 0

    return posture_scores
