# -*- coding: utf-8 -*-
"""
Computes metrics for analyzing a collection of structured data.
@ author Jesper Kristensen
Copyright 2018
"""
import logging
from random import randint
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

__all__ = ["ErgoMetrics"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

logger = logging.getLogger()

class ErgoMetrics(object):
    """
    Computes ergonomics metrics.
    """

    _collection_structured_data_obj = None
    _yaws = None
    _rolls = None
    _pitches = None
    _duration = None
    _speed = None
    _speedNormal = None
    _speedScore = None
    _strain = None
    _posture = None
    _totalScore = None
    _events = None

    def __init__(self, collection_structured_data_obj=None):
        """
        Constructs an object from which metrics can be computed
        based off of a "Collection of Structured Data" object.
        :param experiment_obj:
        """
        self._collection_structured_data_obj = collection_structured_data_obj

        self._yaws = self._collection_structured_data_obj._yaw
        self._pitches = self._collection_structured_data_obj._pitch
        self._rolls = self._collection_structured_data_obj._roll
        self._duration = self.durChecker(self._collection_structured_data_obj)

        # chunks = chunkify(self._pitches['delta'], self._yaws['delta'], self._rolls['delta'])

        motions = []
        posts = []
        speeds = []
        for pitch, yaw, roll in self.chunkify(lists=[self._pitches['delta'],
                                                     self._yaws['delta'],
                                                     self._rolls['delta']],
                                              percent=20):
            # for each percent-sized-chunk
            # (20 % means splitting the list into five chunks, etc.)

            # pitchScore, yawScore, rollScore, totalScore
            motions.append(self.motionScore(pitch=pitch, yaw=yaw, roll=roll))
            speeds.append(self.velcro(pitch=pitch, yaw=yaw, roll=roll))
            self.postScore(pitch=pitch, yaw=yaw, roll=roll,
                                        safe=30)
        logger.info("Generating scores")
        mots = np.array(motions)

        # compute means:
        mot1 = np.mean(mots[:, 0])  # pitchScore
        mot2 = np.mean(mots[:, 1])  # yawScore
        mot3 = np.mean(mots[:, 2])  # rollScore
        mot4 = np.mean(mots[:, 3])  # totalScore

        self._strain = [mot1, mot2, mot3, mot4]
        speedz = np.array(speeds)
        self._speed = [(np.mean(speedz[:, 0])), (np.mean(speedz[:, 1])),
                       (np.mean(speedz[:, 2]))]
        self._speedNormal = [self._speed[0]/21, self._speed[1]/21, self._speed[2]/21]
        self._speedScore = max(self._speedNormal)
        self._totalScore = (self._speedScore + self._strain[3] + self._posture[3])/2

    @property
    def posture(self):
        return self._posture

    @property
    def speed(self):
        return self._speed

    def durChecker(self, exper=None):
        lenz = len(exper.yaw())
        dura = lenz / 10
        dura = dura / 60  # gives minutes
        return dura

    def chunkify(self, lists=None, percent=None):
        """
        Yield successive chunks from the lists based on the percentage wanted.
        For example, if percent = 20, then each list in "lists" is broken into
        five consecutive pieces as such:
        lists = [[1,2,3,4,5], [10,20,30,40,50]] (as an example)
        return (on each yield):
            [1, 10]
            [2, 20]
            ...
            [5, 50]
        """
        lists = np.atleast_1d(lists)

        len_ = len(lists[0])
        n = int(percent / 100 * len_)

        for l in lists:
            if not len(l) == len_:
                raise Exception("Data is not the same size?")

        for i in range(0, len_, n):
            chunks_from_all_lists = [l[i:i + n] for l in lists]
            yield chunks_from_all_lists

    def velcro(self, pitch=None, yaw=None, roll=None):
        """
        """
        yawgradient=np.gradient(yaw)
        pitchgradient=np.gradient(pitch)
        rollgradient=np.gradient(roll)
        try:
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
        except Exception:
            msg = "Failure occured while checking value " + str(n)
            logger.error(msg)
            raise Exception(msg)

        return [np.std(pitch)*7, np.std(yaw)*7, np.std(roll)*7]

    def postScore(self, pitch, yaw, roll, safe):
        """Takes three lists of values, yaw pitch and roll, and calculates posture score
        as percent of time spent outside of a 'safe' posture"""
        totalVals = 0
        unsafe = 0
        n = 0
        pitchn = 0
        yawn = 0
        rolln = 0
        while n < len(pitch):
            if yaw[n] > safe or pitch[n] > safe or roll[n] > safe:
                unsafe = unsafe + 1
                if yaw[n] > safe:
                    yawn = yawn+1
                if roll[n] > safe:
                    rolln = rolln+1
                if pitch[n] > safe:
                    pitchn = pitchn+1
            totalVals = totalVals + 1
            n = n + 1
        postScores = [(7 * pitchn / totalVals), (7 * yawn / totalVals), (7 * rolln / totalVals), (7 * unsafe / totalVals)]
        self._posture = postScores

    def _digitize_values(self, values=None, bins=None):
        """
        Digitizes a set of values into the bins given.
        :param values:
        :param bins:
        :return:
        """
        values_dig = np.digitize(np.abs(values), bins)
        tmp = [0] * len(bins)
        for val in values_dig:
            tmp[val] += 1
        return tmp

    def motionScore(self, pitch=None, yaw=None, roll=None):
        """
        Pass lists of Yaw, Pitch, Roll, returns yaw, pitch, roll, and
        total motion scores.
        """

        bins = [15 * i for i in range(11)]
        pitchBins = self._digitize_values(values=np.abs(pitch), bins=bins)
        yawBins = self._digitize_values(values=np.abs(yaw), bins=bins)
        rollBins = self._digitize_values(values=np.abs(roll), bins=bins)

        yawScore = self.scoreBins(yawBins)
        pitchScore = self.scoreBins(pitchBins)
        rollScore = self.scoreBins(rollBins)

        adjuster = 1200 / len(yaw)
        yawScore = yawScore * adjuster
        pitchScore = pitchScore * adjuster
        rollScore = rollScore * adjuster
        totalScore = yawScore + pitchScore + rollScore
        totalScore = totalScore / 2214

        return pitchScore, yawScore, rollScore, totalScore

    def scoreBins(self, bins=None):
        n = 0
        score = 0
        while n < len(bins):
            contents = bins[n]  # how many counts in this bin?
            total = contents * n
            score += total
            n += 1

        return score
