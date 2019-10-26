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


def compute_posture_score(delta_pitch=None, delta_yaw=None,
                          delta_roll=None, safe_threshold=None):
    """
    Takes values of yaw, pitch, and roll, and calculates posture score
    as percent of time spent outside of a "safe" posture degree value.
    """
    # This score is inherently on a scale of 0-1 so does not need
    # datasets to calibrate - however, if we want to turn this into
    # a weighted score (which is very possible) then we would need them

    # Whenever any of the delta angles extend beyond the safe region,
    # count that as an unsafe event:
    num_unsafe = len(np.where((absolute(delta_pitch) > safe_threshold) | 
                              (absolute(delta_yaw) > safe_threshold) | 
                              (absolute(delta_roll) > safe_threshold))[0])
    
    num_yaw = len(np.where(absolute(delta_yaw) > safe_threshold)[0])
    num_pitch = len(np.where(absolute(delta_pitch) > safe_threshold)[0])
    num_roll = len(np.where(absolute(delta_roll) > safe_threshold)[0])

    num_total = len(delta_yaw)

    # summarize posture scores
    posture_scores = dict(yaw_raw=num_yaw / num_total,
                          pitch_raw=num_pitch / num_total,
                          roll_raw=num_roll / num_total,
                          unsafe_raw=num_unsafe / num_total)

    posture_scores['yaw'] = posture_scores['yaw_raw'] * 7
    posture_scores['pitch'] = posture_scores['pitch_raw'] * 7
    posture_scores['roll'] = posture_scores['roll_raw'] * 7
    posture_scores['unsafe'] = posture_scores['unsafe_raw'] * 7

    return posture_scores
