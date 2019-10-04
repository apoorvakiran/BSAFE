# -*- coding: utf-8 -*-
"""
Computes the posture score among the Iterate Labs Ergo Metrics.

@ author Jacob Tyrrell and Jesper Kristensen
Copyright Iterate Labs 2018-
"""

__all__ = ["compute_posture_score"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"


def compute_posture_score(delta_pitch=None, delta_yaw=None, delta_roll=None, safe=None):
    """
    Takes values of yaw, pitch, and roll, and calculates posture score
    as percent of time spent outside of a "safe" posture degree value.
    """
    totalVals = 0
    unsafe = 0
    n = 0
    pitchn = 0
    yawn = 0
    rolln = 0
    while n < len(delta_pitch):
        if delta_yaw[n] > safe or delta_pitch[n] > safe or delta_roll[n] > safe:
            unsafe = unsafe + 1
            if delta_yaw[n] > safe:
                yawn = yawn+1
            if delta_roll[n] > safe:
                rolln = rolln+1
            if delta_pitch[n] > safe:
                pitchn = pitchn+1
        totalVals = totalVals + 1
        n = n + 1
    postScores = [(7 * pitchn / totalVals), (7 * yawn / totalVals),
                    (7 * rolln / totalVals), (7 * unsafe / totalVals)]
    return postScores
