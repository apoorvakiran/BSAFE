# -*- coding: utf-8 -*-
"""
Computes metrics for analyzing the data.

@ author Jesper Kristensen
Copyright 2018
"""

from random import randint
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

__all__ = ["Metrics", "velcro", "motionScore"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"


class Metrics(object):
    """
    Takes an experiment object and creates + stores a list of events
    """

    _experiment = None
    _yaws = None
    _rolls = None
    _pitches = None
    _duration = None
    _speed = None
    _motion = None
    _posture = None
    _events = None

    def __init__(self, exper=None):
        self._experiment = exper
        self._yaws = exper._yaw
        self._pitches = exper._pitch
        self._rolls = exper._roll
        self._duration = durChecker(exper)
        #self._posture = postScore(self._yaws['delta'], self._pitches['delta'], self._rolls['delta'], 30)
        #self._speed = velcro(exper)
        #self._motion = motionScore(self._yaws['delta'], self._pitches['delta'], self._rolls['delta'])
        #self._events = eventFinder(self, 30)
        chunks = chunkify(self._pitches['delta'], self._yaws['delta'], self._rolls['delta'])
        motions =[]
        posts = []
        speeds = []
        for chunk in chunks:
            motions.append(motionScore(chunk[0],chunk[1],chunk[2]))
            speeds.append(velcro(chunk[0], chunk[1], chunk[2]))
            posts.append(postScore(chunk[0], chunk[1], chunk[2], 30))
        self._posture = np.mean(posts)
        mots = np.array(motions)
        #print(motions)
        mot1=np.mean(mots[:,0])
        mot2 = np.mean(mots[:, 1])
        mot3 = np.mean(mots[:, 2])
        mot4 = np.mean(mots[:, 3])
        self._motion = [mot1, mot2, mot3, mot4]
        speedz = np.array(speeds)
        self._speed = [(np.mean(speedz[:, 0])), (np.mean(speedz[:, 1])), (np.mean(speedz[:, 2]))]


def durChecker(exper):
    lenz = len(exper.yaw())
    dura = lenz/10
    dura = dura/60#gives minutes
    return(dura)


def velcro(pitch, yaw, roll):
    """
    exp needs to be of type experiment or event
    """
    yawgradient=np.gradient(yaw)
    pitchgradient=np.gradient(pitch)
    rollgradient=np.gradient(roll)
    try:
        n=0
        yaw=[]
        pitch=[]
        roll=[]
        while n < len(yawgradient):
            if yawgradient[n] < 100:
                yaw.append(yawgradient[n])
            if pitchgradient[n] < 100:
                pitch.append(pitchgradient[n])
            if rollgradient[n] < 100:
                roll.append(rollgradient[n])
            n=n+1
    except:
        print("Failure occured while checking value " + str(n))
    return [np.std(pitch), np.std(yaw), np.std(roll)]


def postScore(pitch, yaw, roll, safe):
    """
    Takes three lists of values, yaw pitch and roll, and calculates posture score
    as percent of time spent outside of a 'safe' posture
    """
    totalVals=0
    unsafe=0
    for val in yaw:
        if val > safe:
            unsafe=unsafe+1
        totalVals=totalVals+1
    for val in pitch:
        if val > safe:
            unsafe=unsafe+1
        totalVals=totalVals+1
    for val in roll:
        if val > safe:
            unsafe = unsafe+1
        totalVals=totalVals+1
    return(unsafe/totalVals)


def motionScore (pitch, yaw, roll):
    """
    Pass lists of Yaw, Pitch, Roll, returns yaw, pitch, roll, and total motion scores
    """
    yawBins=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for value in yaw:
        try:
            abV=np.abs(value)
            bin=int(abV/15)
            yawBins[bin]=yawBins[bin]+1
        except:
            print("Yaw Bin")
            print(value)
    rollBins = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for value in roll:
        try:
            abV = np.abs(value)
            bin = int(abV / 15)
            rollBins[bin] = rollBins[bin] + 1
        except:
            print("Roll Bin")
            print(value)
    pitchBins = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for value in pitch:
        try:
            abV = np.abs(value)
            bin = int(abV / 15)
            pitchBins[bin] = pitchBins[bin] + 1
        except:
            pass
    yawScore=scoreBins(yawBins)
    pitchScore=scoreBins(pitchBins)
    rollScore=scoreBins(rollBins)
    adjuster=1200/len(yaw)
    yawScore = yawScore*adjuster
    pitchScore = pitchScore * adjuster
    rollScore = rollScore * adjuster
    totalScore = yawScore + pitchScore + rollScore
    totalScore = totalScore/2214
    return [pitchScore, yawScore, rollScore, totalScore]

def scoreBins(bins):

    n = 0
    score = 0
    while n < len(bins):
        contents = bins[n]
        total = contents*n
        score = score+total
        n=n+1
    return score


def chunkify(pitch, yaw, roll):

    sets=[]
    n = 0
    lenny = len(pitch)
    chunks = max(8,int(lenny / 9000))
    #print (chunks)
    while n < chunks:
        nines = n * 9000
        samples = []
     # print(nines)
        for something in np.arange(0, 4, 1):
            samples.append(randint(nines, nines + 9000))
        for samp in samples:
            thisYaSample = pitch[samp:(samp + 1200)]
            thisPiSample = yaw[samp:(samp + 1200)]
            thisRollSample = roll[samp:(samp+1200)]
            #print(np.std(thisYaSample))
            if (np.std(thisYaSample)>10 and np.std(thisPiSample)>10 and np.std(thisRollSample) > 10):
                 sets.append([thisPiSample, thisYaSample, thisRollSample])
        n = n + 1
    print(sets)
    return sets
