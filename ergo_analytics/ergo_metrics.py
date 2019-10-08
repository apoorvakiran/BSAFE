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
from .metrics import compute_posture_score
from .metrics import compute_motion_score
from .metrics import compute_velocity_score

logger = logging.getLogger()


class ErgoMetrics(object):
    """
    Computes Ergonomic Metrics (ErgoMetrics) for the incoming data
    which is assumed to be in "structured" form as opposed to "raw" data.
    
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

        # ergoMetrics currently just cares about delta values:
        self._delta_yaw = self._data.get_data(type='yaw', loc='delta')
        self._delta_pitch = self._data.get_data(type='pitch', loc='delta')
        self._delta_roll = self._data.get_data(type='roll', loc='delta')

        self._scores = dict()

    def compute(self):
        """
        Compute the ergo metric scores - the ergoScores if you will.
        """
        # compute the scores
        logger.debug("Computing ErgoMetric scores...")

        motion_score = compute_motion_score(delta_pitch=self._delta_pitch,
                                            delta_yaw=self._delta_yaw,
                                            delta_roll=self._delta_roll)

        speed_score_tmp = compute_velocity_score(delta_pitch=self._delta_pitch,
                                             delta_yaw=self._delta_yaw,
                                             delta_roll=self._delta_roll)

        posture_score = compute_posture_score(delta_pitch=self._delta_pitch,
                                      delta_yaw=self._delta_yaw,
                                      delta_roll=self._delta_roll, safe=30)
        
        # re-define some new variable names:
        raw_strain = motion_score
        raw_speed = speed_score_tmp

        # normalize the speed:
        normalized_speed = self._normalize_speed(speed=raw_speed)
        speed_score = self._compute_speed_score(speed=normalized_speed)

        scores = {'speed': speed_score, 'strain': raw_strain,
                  'posture': posture_score}
        total_score = self._compute_total_score(scores=scores)
        
        scores['total'] = total_score

        self._scores.update(**scores)

    @staticmethod
    def _compute_total_score(scores=None):
        """
        Computes the total score from the incoming scores.
        """
        # combine the speed score with the total scores from strain and posture:
        return (scores['speed'] + scores['strain'][3] + scores['posture'][3]) / 2

    @staticmethod
    def _normalize_speed(speed=None):
        """
        Normalizes the speed.
        """
        return np.asarray(speed) / 21

    @staticmethod
    def _compute_speed_score(speed=None):
        """
        Compute the speed score given potentially normalized speeds.
        """
        return max(speed)

    def get_score(self, name='total'):
        """
        Returns the score with "name".
        """
        if len(self._scores) == 0:
            raise Exception("Please compute the Ergo Metrics scores first!\n"
                            "Do this by calling the .compute() method.")
        if name not in self._scores:
            raise Exception("Was unable to find the score with name '{}'\n \
                valid options are: {}".format(name, list(self._scores.keys())))
        
        return self._scores[name]
