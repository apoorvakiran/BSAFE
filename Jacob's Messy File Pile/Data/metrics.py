"""
Creates an object that contains scores for a given experiment object - Strain, Speed, Posture, and Total
"""
import numpy as np
from random import randint

class Metrics(object):
    """Takes an experiment object and creates + stores a list of events"""
    _experiment = None
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
    _name = None

    def __init__(self, exper=None):
        self._experiment = exper
        self._yaws = exper._yaw
        self._pitches = exper._pitch
        self._rolls = exper._roll
        self._duration = self.durChecker(exper)
        self._name = exper.name.replace('_', ',')
        # self._posture = postScore(self._yaws['delta'], self._pitches['delta'], self._rolls['delta'], 30)
        # self._speed = velcro(exper)
        # self._strain = strainScore(self._yaws['delta'], self._pitches['delta'], self._rolls['delta'])
        # self._events = eventFinder(self, 30)
        chunks = self.chunkify(self._pitches['delta'], self._yaws['delta'], self._rolls['delta'])
        strains = []
        posts = []
        speeds = []
        for chunk in chunks:
            strains.append(self.strainScore(chunk[0], chunk[1], chunk[2]))
            speeds.append(self.velcro(chunk[0], chunk[1], chunk[2]))
            posts.append(self.postScore(chunk[0], chunk[1], chunk[2], 30))
        self._posture = np.mean(posts)
        try:
            mots = np.array(strains)
            # print(strains)
            mot1 = np.mean(mots[:, 0])
            mot2 = np.mean(mots[:, 1])
            mot3 = np.mean(mots[:, 2])
            mot4 = np.mean(mots[:, 3])
            self._strain = [mot1, mot2, mot3, mot4]
        except:
            print("Failure at generating strain scores for " + exper.name)
            print("Trying again")
            try:
                mots = np.array(strains)
                # print(strains)
                mot1 = np.mean(mots[:, 0])
                mot2 = np.mean(mots[:, 1])
                mot3 = np.mean(mots[:, 2])
                mot4 = np.mean(mots[:, 3])
                self._strain = [mot1, mot2, mot3, mot4]
            except:
                print("Failure again")
                self._strain = [0, 0, 0, 0]
        speedz = np.array(speeds)
        self._speed = [(np.mean(speedz[:, 0])), (np.mean(speedz[:, 1])), (np.mean(speedz[:, 2]))]
        self._speedNormal = [self._speed[0] / 21, self._speed[1] / 21, self._speed[2] / 21]
        self._speedScore = max(self._speedNormal)
        self._totalScore = (self._speedScore + self._strain[3] + self._posture) / 2

    def durChecker(self, exper):
        lenz = len(exper.yaw())
        dura = lenz / 10
        dura = dura / 60  # gives minutes
        return (dura)

    def velcro(self, pitch, yaw, roll):
        yawgradient = np.gradient(yaw)
        pitchgradient = np.gradient(pitch)
        rollgradient = np.gradient(roll)
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
                n = n + 1
        except:
            print("Failure occured while checking value " + str(n))
        return [np.std(pitch), np.std(yaw), np.std(roll)]

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
        postScore = [7 * pitchn / totalVals, 7 * yawn / totalVals, 7 * rolln / totalVals, 7 * unsafe / totalVals]
        return postScore

    def strainScore(self, pitch, yaw, roll):
        """pass lists of Yaw, Pitch, Roll, returns yaw, pitch, roll, and total strain scores"""
        yawBins = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for value in yaw:
            try:
                abV = np.abs(value)
                bin = int(abV / 15)
                yawBins[bin] = yawBins[bin] + 1
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
        yawScore = self.scoreBins(yawBins)
        pitchScore = self.scoreBins(pitchBins)
        rollScore = self.scoreBins(rollBins)
        adjuster = 1200 / len(yaw)
        yawScore = yawScore * adjuster
        pitchScore = pitchScore * adjuster
        rollScore = rollScore * adjuster
        totalScore = yawScore + pitchScore + rollScore
        totalScore = totalScore / 2214
        return [pitchScore, yawScore, rollScore, totalScore]

    def scoreBins(self, bins):
        n = 0
        score = 0
        while n < len(bins):
            contents = bins[n]
            total = contents * n
            score = score + total
            n = n + 1
        return score

    def chunkify(self, pitch, yaw, roll):
        sets = []
        n = 0
        lenny = len(pitch)
        chunks = max(8, int(lenny / 9000))
        # print (chunks)
        while n < chunks:
            nines = n * 9000
            samples = []
            # print(nines)
            for something in np.arange(0, 4, 1):
                samples.append(randint(nines, nines + 9000))
            for samp in samples:
                thisYaSample = pitch[samp:(samp + 1200)]
                thisPiSample = yaw[samp:(samp + 1200)]
                thisRollSample = roll[samp:(samp + 1200)]
                # print(np.std(thisYaSample))
                if (np.std(thisYaSample) > 10 and np.std(thisPiSample) > 10 and np.std(thisRollSample) > 10):
                    sets.append([thisPiSample, thisYaSample, thisRollSample])
            n = n + 1
        # print(sets)
        return sets
