"""
Creates an avatar which presents a worker performing a task.
Will take information on angles and frequencies of motions in... some format
Creates a dummy dataset representing a worker performing within that range of motions.
"""

__all__ = ["Avatar"]

import numpy as np

class Avatar(object):

    name = None
    _freq = None
    _yaw = None #list of yaw results generated
    _roll = None #list of roll results generated
    _pitch = None #list of pitch results generated
    #the above three will be lists of lists. A list of values will be generated and appended when simulate is called

    def __init__(self, name = None, dicta = None):
       self._yaw = []
       self._roll = []
       self._pitch = []
       self._freq = []
       self.name = name
       if dicta is not None:
           self.generate(dicta)

    #generate Takes a dictionary
    #:param self:
    #:param dicty: Dictionary containing entries for
    #yaw
    #pitch
    #roll
    #time
    #Yaw, pitch, and roll should be given as (mean, standard deviation). If none given, will assume (0.0, 45)
    #Time should be (hours, % time actively working) with percent given between 0 and 1.0

    #name needs to be formatted in "X_X_X_X_X Format"
    #e.g. "Day_Something_Task_Name_Segment_Hand"
    #mimics the experiment type for passing to Results



    def simulate (self, value = None, stDev = None, length = None, type = None):
      """
       Takes a value, 0->2 for yaw, roll, pitch respectively and generates
       values for that of the given length, using a normal distribution
       with standard deviation of stDev
       """
      if value is None:
          return ("Enter a valid location value (0 for yaw, 1 for roll, 2 for pitch)"
                  " to simulate data and valid length of simulation")

      valuable=list(np.random.normal(0, stDev, length))
      if value == 0:
          if type == 1:
              valuable = self.sortPoints(valuable)
          self._yaw = self._yaw + valuable
      if value == 1:
          if type == 1:
              valuable = self.sortPoints(valuable)
          self._roll = self._roll +valuable
      if value == 2 :
          if type == 1:
              valuable = self.sortPoints(valuable)
          self._pitch = self._pitch + valuable


    def generate(self, dicty = None):
        """
        Takes a dictionary
        :param self:
        :param dicty: Dictionary containing entries for
        yaw
        pitch
        roll
        time
        freq
        Yaw, pitch, and roll should be given as (mean, standard deviation). If none given, will assume (0.0, 45)
        Time should be (hours, % time actively working) with percent given between 0 and 1.0
        frequency will be the number of oscillations per minute, and should contain an int
        :return:
        """
        hours = dicty['time'][0]
        active = dicty['time'][1]
        yawdev = dicty['yaw'][1]
        pitchdev = dicty['pitch'][1]
        rolldev = dicty['roll'][1]
        frequent = dicty['freq']
        self._freq = frequent
        #assume: breaks are evenly spaced within each hour of work
        workSegment= int(active * 36000)
        breakSegment = int((1-active) * 36000)
        #start with a short period of time of inactivity
        self.simulate(0, 5, 100)
        self.simulate(1, 5, 100)
        self.simulate(2, 5, 100)
        n=0
        while n < hours:
            #simulate the working period from hour n
            self.simulate(0, yawdev, workSegment, 0)
            self.simulate(1, rolldev, workSegment, 0)
            self.simulate(2, pitchdev, workSegment, 0)
            #add a break period for hour n
            self.simulate(0, 5, breakSegment, 1)
            self.simulate(1, 5, breakSegment, 1)
            self.simulate(2, 5, breakSegment, 1)
            #move to hour n+1
            n = n+1
       #simulate short period of endtime inactivity
        self.simulate(0, 5, 100, 1)
        self.simulate(1, 5, 100, 1)
        self.simulate(2, 5, 100, 1)

    def yaw (self, delta = None):
        """
        Set of grabbers designed to mimic the experiment type object, for processing
        as a results object.
        :param delta:
        :return:
        """
        return self._yaw

    def roll (self, delta = None):
        """
        Set of grabbers designed to mimic the experiment type object, for processing
        as a results object.
        :param delta:
        :return:
        """
        return self._roll

    def pitch (self, delta = None):
        """
        Set of grabbers designed to mimic the experiment type object, for processing
        as a results object.
        :param delta:
        :return:
        """
        return self._pitch

    def quadCorrect(self, value):
        pass

    def topAndBottom(self):
        pass

    def get_data(self):
        return self._yaw

    def sortPoints(self, arrayz):
        """
        Takes an array of points generated using np.random.normal
        organizes it from low to high
        removes values that are out of range
        and then creates a series of cycles with byFreq
        that is then returned.
        :param arrayz: np.array object
        :return: np.array object
        """
        arrayz.sort()
        start = 0
        res = -1000
        while res < -90:
            res = arrayz[start]
            start = start+1
        stop = -1
        res=1000
        while res > 90:
            res = arrayz[stop]
            stop = stop-1
        arrayz = arrayz[start:stop]
        return self.byFreq(arrayz)


    def byFreq (self, arr):
        """
        Takes an array of points and sorts them into a series of rises and falls
        with a frequency equivalent to self._freq cycles per minute.
        :param arr:
        :return:
        """
        freqs = self._freq
        #freqs is cycles per minute
        #600 array items per minute
        #So a cycle should be 600/freqs entries long, top to bottom to top again?
        #Single top to bottom length will be half that.
        lens = len(arr)
        print(lens)
        halfCycle = 300/freqs
        runs = int(lens/halfCycle) #not a full cycle but a run from top to bottom
        halfsies = []
        sies = 0
        while sies < runs:
            halfsies.append([])
            sies=sies+1
        cycle = 0
        print(len(halfsies))
        for value in arr:

            halfsies[cycle].append(value)
            cycle = cycle + 1
            if cycle == runs:
                cycle = 0
        #all cycles go from bottom to top
        #need to flip every other cycle
        #bottom to top, top to bottom etc
        n = 1
        while n < len(halfsies):
            halfsies[n] = np.flip(halfsies[n])
            n = n+2
        thisRun = []
        for listicle in halfsies:
            print("a run!" + str(thisRun))
            thisRun = thisRun + listicle

        return thisRun















