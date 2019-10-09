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
from .metrics import compute_strain_score
from .metrics import compute_speed_score

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

    @property
    def data(self):
        return self._data

    def compute(self):
        """
        Compute the ergo metric scores - the ergoScores if you will.
        """
        # compute the scores
        logger.debug("Computing ErgoMetric scores...")

        strain_scores_tmp = compute_strain_score(delta_pitch=self._delta_pitch,
                                                 delta_yaw=self._delta_yaw,
                                                 delta_roll=self._delta_roll)

        speed_scores_tmp = compute_speed_score(delta_pitch=self._delta_pitch,
                                               delta_yaw=self._delta_yaw,
                                               delta_roll=self._delta_roll)

        posture_scores_tmp = compute_posture_score(
            delta_pitch=self._delta_pitch, delta_yaw=self._delta_yaw,
            delta_roll=self._delta_roll, safe_threshold=30)

        # finalize speed scores:
        speed_scores = speed_scores_tmp
        # normalize the speed scores:
        self._normalize_speed(speed_scores=speed_scores)
        total_speed_score = self._compute_total_speed_score(
            speed_scores=speed_scores)
        speed_scores['total'] = total_speed_score
        self._scores['speed'] = speed_scores

        # finalize posture scores:
        self._scores['posture'] = posture_scores_tmp

        # finalize strain scores:
        self._scores['strain'] = strain_scores_tmp

        total_score = self._compute_total_score(scores=self._scores)
        self._scores['total'] = total_score

    @staticmethod
    def _compute_total_score(scores=None):
        """
        Computes the total score from the incoming scores.
        """
        # combine the speed score with the total scores from strain and posture:
        return (scores['speed']['total'] + scores['strain']['total'] +
                scores['posture']['unsafe']) / 2

    @staticmethod
    def _normalize_speed(speed_scores=None):
        """
        Normalizes the speed.
        """
        for key in ['yaw', 'pitch', 'roll']:
            speed_scores[key + '_normalized'] = \
                np.asarray(speed_scores[key]) / 21

    @staticmethod
    def _compute_total_speed_score(speed_scores=None):
        """
        Compute the speed score given potentially normalized speeds.
        """
        collected = []
        for key in speed_scores:
            if key.endswith("_normalized"):
                collected.append(speed_scores[key])
        return np.max(collected)

    def get_score(self, name='total'):
        """
        Returns the score with "name".
        """
        if len(self._scores) == 0:
            logger.exception("Please compute the Ergo Metrics scores first!\n"
                             "Do this by calling the .compute() method.")

        scores = self._scores.copy()

        name = name.split('/')
        for n in name:
            if n not in scores:
                logger.exception(f"Was unable to find the score "
                                 f"with name '{n}'")
            try:
                scores = scores[n]
            except:
                import pdb
                pdb.set_trace()

        return scores
