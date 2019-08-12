"""
Take an experiment object, creates a list of hits per period of time given, both in a sum and per axis
"""

class theHits(object):
    """
    Take an experiment object, creates a list of hits per period of time given, both in a sum and per axis
    """
    _experiment = None #experiment object given to the constructor
    _hitparade = None #list of hits per cycle
    _timeFrame = None #number of cycles to average over
    _cycleLength = None #time of a "cycle" for dumb-cycle analysis in seconds
    _hitValue = None

    def __init__(self, exper = None, fTime = None, cLength = None, hitValue = 20):
        self._experiment = exper
        self._timeFrame = fTime
        self._cycleLength = cLength
        self._hitparade = self.parade()
        self._hitValue = hitValue

    def parade (self):
        toView = 10 * self._cycleLength
        parade = []
        n = 0
        pitch = self._experiment.pitch(delta = True)
        yaw = self._experiment.yaw(delta = True)
        roll = self._experiment.roll(delta = True)
        pitchHits = []
        yawHits = []
        rollHits = []
        pitchHit=0
        yawHit=0
        rollHit=0
        while n < len(pitch):
            if n % toView == 0 :
                pitchHits.append(0)
                yawHits.append(0)
                rollHits.append(0)
            if pitch[n] > self.hitValue:
                if pitchHit == 0:
                    pitchHit = 1
                    pitchHits[-1] = pitchHits[-1] + 1
            else:
                if pitchHit == 1:
                    pitchHit = 0
            if yaw[n] > self.hitValue:
                if yawHit == 0:
                    yawHit = 1
                    yawHits[-1] = yawHits[-1] + 1
            else:
                if yawHit == 1:
                    yawHit = 0
            if roll[n] > self.hitValue:
                if rollHit == 0:
                    rollHit = 1
                    rollHits[-1] = pitchHits[-1] + 1
            else:
                if rollHit == 1:
                    rollHit = 0

            n = n + 1
        n = 0
        paradice = [0, 0, 0, 0]
        while n < len(pitchHits) :
            if n % self._timeFrame == 0:
                paradice[3] = paradice[0] + paradice[1] + paradice[2]
                rezzy = [paradice[0]/self._timeFrame, paradice[1]/self._timeFrame, paradice[2]/self._timeFrame,
                         paradice[3]/self._timeFrame]
                parade.append(rezzy)
                paradice = [0, 0, 0, 0]
            paradice[0] = paradice[0] + pitchHits[n]
            paradice[1] = paradice[1] + yawHits[n]
            paradice[2] = paradice[2] + rollHits[n]
            n = n+1
        return parade

