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
    
    # now do similar for yaw, pitch, roll...
    
    import pdb
    pdb.set_trace()

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
    
    return (7 * pitchn / totalVals), (7 * yawn / totalVals), (7 * rolln / totalVals), (7 * unsafe / totalVals)
