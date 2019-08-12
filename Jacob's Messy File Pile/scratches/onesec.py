import numpy as np




class Seconds(object):
    _seconds = None
    _experiment = None

    def __init__(self, expy):
        entries=len(expy.yaw())
        self._seconds = []
        n=0
        self._experiment=expy
        while n < entries:
            nuSec = OneSec(expy, n)
            self._seconds.append(nuSec)
            n = n + 10


class OneSec(object):
    _yaw = None
    _pitch = None
    _roll = None
    _exper = None
    _features = None
    _order = None

    def __init__(self, experiment, starting):
        self._order = starting
        stop = starting + 10
        self._yaw = {}
        self._yaw['hand'] = experiment.yaw(loc='hand')[starting:stop]
        self._yaw['wrist'] = experiment.yaw(loc='wrist')[starting:stop]
        self._yaw['delta'] = experiment.yaw(delta=True)[starting:stop]
        self._roll = {}
        self._roll['hand'] = experiment.roll(loc='hand')[starting:stop]
        self._roll['wrist'] = experiment.roll(loc='wrist')[starting:stop]
        self._roll['delta'] = experiment.roll(delta=True)[starting:stop]
        self._pitch = {}
        self._pitch['hand'] = experiment.pitch(loc='hand')[starting:stop]
        self._pitch['wrist'] = experiment.pitch(loc='wrist')[starting:stop]
        self._pitch['delta'] = experiment.pitch(delta=True)[starting:stop]
        self._exper = experiment
        self._features = self.genfeatures()

    def genfeatures(self):
        meanYawHand=np.mean(self._yaw['hand'])
        meanYawWrist = np.mean(self._yaw['wrist'])
        meanYawDelta = np.mean(self._yaw['delta'])
        meanPitchHand=np.mean(self._pitch['hand'])
        meanPitchWrist = np.mean(self._pitch['wrist'])
        meanPitchDelta = np.mean(self._pitch['delta'])
        meanRollHand=np.mean(self._roll['hand'])
        meanRollWrist = np.mean(self._roll['wrist'])
        meanRollDelta = np.mean(self._roll['delta'])
        stdYawHand=np.std(self._yaw['hand'])
        stdYawWrist = np.std(self._yaw['wrist'])
        stdYawDelta = np.std(self._yaw['delta'])
        stdPitchHand=np.std(self._pitch['hand'])
        stdPitchWrist = np.std(self._pitch['wrist'])
        stdPitchDelta = np.std(self._pitch['delta'])
        stdRollHand=np.std(self._roll['hand'])
        stdRollWrist = np.std(self._roll['wrist'])
        stdRollDelta = np.std(self._roll['delta'])
        zeroesYawHand=self.zeroes(self._yaw['hand'])
        zeroesYawWrist = self.zeroes(self._yaw['wrist'])
        zeroesYawDelta = self.zeroes(self._yaw['delta'])
        zeroesPitchHand=self.zeroes(self._pitch['hand'])
        zeroesPitchWrist = self.zeroes(self._pitch['wrist'])
        zeroesPitchDelta = self.zeroes(self._pitch['delta'])
        zeroesRollHand=self.zeroes(self._roll['hand'])
        zeroesRollWrist = self.zeroes(self._roll['wrist'])
        zeroesRollDelta = self.zeroes(self._roll['delta'])
        maxYawHand=max(self._yaw['hand'])
        maxYawWrist = max(self._yaw['wrist'])
        maxYawDelta = max(self._yaw['delta'])
        maxPitchHand=max(self._pitch['hand'])
        maxPitchWrist = max(self._pitch['wrist'])
        maxPitchDelta = max(self._pitch['delta'])
        maxRollHand=max(self._roll['hand'])
        maxRollWrist = max(self._roll['wrist'])
        maxRollDelta = max(self._roll['delta'])
        speed = self.velcro(self._pitch['delta'], self._yaw['delta'], self._roll['delta'])
        motion = self.motionScore(self._pitch['delta'], self._yaw['delta'], self._roll['delta'])
        features = [meanYawHand, meanYawWrist, meanYawDelta, meanPitchHand, meanPitchWrist, meanPitchDelta, meanRollHand,
                    meanRollWrist, meanRollDelta, stdYawHand, stdYawWrist, stdYawDelta, stdPitchHand, stdPitchWrist,
                    stdPitchDelta, stdRollHand, stdRollWrist, stdRollDelta, zeroesYawHand, zeroesYawWrist,
                    zeroesYawDelta, zeroesPitchHand, zeroesPitchWrist, zeroesPitchDelta, zeroesRollHand, zeroesRollWrist,
                    zeroesRollDelta, maxYawHand, maxYawWrist, maxYawDelta, maxPitchHand, maxPitchWrist, maxPitchDelta,
                    maxRollHand, maxRollWrist, maxRollDelta, speed[0],speed[1],speed[2], motion[0], motion[1], motion[2], motion[3]]
        return features



    def velcro(self,pitch, yaw, roll):
        '''exp needs to be of type experiment or event'''
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


    def motionScore(self, pitch, yaw, roll):
        """pass lists of Yaw, Pitch, Roll, returns yaw, pitch, roll, and total motion scores"""
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
        adjuster = 120
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

    def zeroes(self, angles):
        zeroCrossings = 0
        previousangle = 0
        for value in angles:
            minAngle=min(value, previousangle)
            maxAngle=max(value, previousangle)
            if minAngle < 0 < maxAngle:
                zeroCrossings=zeroCrossings+1
            previousangle=value
        return zeroCrossings



