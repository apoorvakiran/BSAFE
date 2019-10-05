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


def compute_posture_score(delta_pitch=None, delta_yaw=None, delta_roll=None, safe=None):
    """
    Takes values of yaw, pitch, and roll, and calculates posture score
    as percent of time spent outside of a "safe" posture degree value.
    """
    
    # Whenever any of the delta angles extend beyond the safe region,
    # count that as an unsafe event:
    num_unsafe = len(np.where((absolute(delta_pitch) > safe) | 
                              (absolute(delta_yaw) > safe) | 
                              (absolute(delta_roll) > safe))[0])
    
    num_yaw = len(np.where(absolute(delta_yaw) > safe)[0])
    num_pitch = len(np.where(absolute(delta_pitch) > safe)[0])
    num_roll = len(np.where(absolute(delta_roll) > safe)[0])

    num_total = len(delta_yaw)
    
    # adjustments:
    yaw_posture_score = 7 * num_yaw / num_total
    pitch_posture_score = 7 * num_pitch / num_total
    roll_posture_score = 7 * num_roll / num_total
    unsafe_score = 7 * num_unsafe / num_total

    return pitch_posture_score, yaw_posture_score, roll_posture_score, unsafe_score
