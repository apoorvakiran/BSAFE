# -*- coding: utf-8 -*-
"""
Computes metrics for analyzing a collection of structured data.

@ author Jesper Kristensen with Iterate Labs, Inc.
Copyright 2018
"""

__all__ = ["ErgoMetrics"]
__author__ = "Iterate Labs, Inc."
__version__ = "Alpha"

import numpy as np
import logging
from ErgoAnalytics.ErgoMetric_Scores import compute_posture_score
from ErgoAnalytics.ErgoMetric_Scores import compute_motion_score
from ErgoAnalytics.ErgoMetric_Scores import compute_velocity_score

logger = logging.getLogger()


class ErgoMetrics(object):
    """
    Computes Ergonomic Metrics (ErgoMetrics) for the incoming data.
    
    The Ergo Metrics is what is responsible for creating the ergonomics
    scores and provide an evaluation for management and people in
    charge of the safety.
    """

    _data = None
    _delta_yaw = None
    _delta_pitch = None
    _delta_roll = None
    _scores = None

    def __init__(self, structured_data=None):
        """
        Constructs an object from which metrics can be computed
        based off of a "Structured Data" object.

        :param structured_data:
        """

        self._data = structured_data
        
        # get the data we need
        self._delta_yaw = self._data.yaw(delta=True)
        self._delta_pitch = self._data.pitch(delta=True)
        self._delta_roll = self._data.roll(delta=True)

        self._scores = dict()
    
    def compute(self):
        """
        Compute the ergo metric scores.
        """
        # compute the scores
        logger.debug("Computing ErgoMetric scores...")

        motion_score = compute_motion_score(delta_pitch=self._delta_pitch,
                                            delta_yaw=self._delta_yaw,
                                            delta_roll=self._delta_roll)

        speed_score = compute_velocity_score(delta_pitch=self._delta_pitch,
                                             delta_yaw=self._delta_yaw,
                                             delta_roll=self._delta_roll)

        posture_score = compute_posture_score(delta_pitch=self._delta_pitch,
                                      delta_yaw=self._delta_yaw,
                                      delta_roll=self._delta_roll, safe=30)
        
        # mots = np.array(motion_score)

        # # compute means:
        # mot1 = np.mean(mots[:, 0])  # pitchScore
        # mot2 = np.mean(mots[:, 1])  # yawScore
        # mot3 = np.mean(mots[:, 2])  # rollScore
        # mot4 = np.mean(mots[:, 3])  # totalScore

        # self._strain = [mot1, mot2, mot3, mot4]

        # speedz = np.array(speeds)

        # self._speed = [(np.mean(speedz[:, 0])), (np.mean(speedz[:, 1])),
        #                (np.mean(speedz[:, 2]))]
        # self._speedNormal = [self._speed[0]/21, self._speed[1]/21, self._speed[2]/21]
        # self._speedScore = max(self._speedNormal)
        # self._totalScore = (self._speedScore + self._strain[3] + self._posture[3])/2

    @property
    def score(self, name='posture'):
        """
        Returns the score with "name".
        """
        if len(self._scores) == 0:
            raise Exception("Please compute the Ergo Metrics scores first!")
        if name not in self._scores:
            raise Exception("Was unable to find the score with name '{}'\n \
                valid options are: {}".format(name, list(self._scores.keys())))
        
        return self._scores[name]
