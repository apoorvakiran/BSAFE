# -*- coding: utf-8 -*-
"""
Computes the posture score among the Iterate Labs Ergo Metrics.

@ author Jacob Tyrrell and Jesper Kristensen
Copyright Iterate Labs 2018-
"""

__all__ = ["compute_velocity_score"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

from numpy import gradient
from numpy import std
import logging

logger = logging.getLogger()


def compute_velocity_score(delta_pitch=None, delta_yaw=None, delta_roll=None):
    """
    Computes the velocity score.
    """
    yawgradient = gradient(delta_yaw)
    pitchgradient = gradient(delta_pitch)
    rollgradient = gradient(delta_roll)

    n = 0
    yaw = []
    pitch = []
    roll = []
    while n < len(yawgradient):

        if yawgradient[n] < 100:
            yaw.append(yawgradient[n])
        if pitchgradient[n] < 100:
            pitch.append(pitchgradient[n])
        if rollgradient[n] < 100:
            roll.append(rollgradient[n])

        n += 1
    
    return std(pitch) * 7, std(yaw) * 7, std(roll) * 7
