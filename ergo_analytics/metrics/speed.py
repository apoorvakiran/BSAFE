# -*- coding: utf-8 -*-
"""
Computes the posture score among the Iterate Labs Ergo Metrics.

@ author Jesper Kristensen and Jacob Tyrrell
Copyright Iterate Labs 2018-
"""

__all__ = ["compute_speed_score"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

from numpy import gradient
from numpy import absolute
from numpy import std
import logging

logger = logging.getLogger()


def compute_speed_score(delta_pitch=None, delta_yaw=None, delta_roll=None):
    """
    Computes the velocity score.

    First, velocity is approximated as the gradient of the angle in time. We imagine
    this creating a distribution of instantenous values. When this distribution is
    wide it means that we see many high-valued velocities.
    So the wider / higher std dev the higher the score should be.
    
    This measures the width of the distribution of instantenous velocities.
    """

    if len(delta_yaw) < 10:
        # do not compute gradients (not enough data)
        return 0, 0, 0

    gradient_yaw = gradient(delta_yaw)
    gradient_pitch = gradient(delta_pitch)
    gradient_roll = gradient(delta_roll)

    THRESHOLD_GRAD = 100
    #
    std_yaw = gradient_yaw[absolute(gradient_yaw) < THRESHOLD_GRAD].std()
    std_pitch = gradient_pitch[absolute(gradient_pitch) < THRESHOLD_GRAD].std()
    std_roll = gradient_roll[absolute(gradient_roll) < THRESHOLD_GRAD].std()

    # summarize speed scores
    speed_scores = dict(yaw_raw=std_yaw, pitch_raw=std_pitch, roll_raw=std_roll)
    speed_scores['yaw'] = speed_scores['yaw_raw'] * 7
    speed_scores['pitch'] = speed_scores['pitch_raw'] * 7
    speed_scores['roll'] = speed_scores['roll_raw'] * 7

    return speed_scores
