"""
Goal:
establish a type that can take an experiment
and parse out what I'll be calling *events*.
An event will be a time when flexion goes above 30 degrees
in one or more axis, lasting until all three measures go
down to a safe range.
Caveats: Requires that our data is zero centered.
Apoorva has been working with data such that he subtracts the mean from all
values, to adjust towards the center of 0.
This requires the assumption that 0 is the correct mean (should be true?).
So far this seems to have been working out.

@author Jacob Tyrrell
"""

import numpy as np
from . import ergoMetrics, velcro, motionScore


def eventFinder(eventual, angle):
    """Feed an events object, return a list of individual event objects.
    Assumption: Values in the experiment are held in order of timing."""
    #So an event is a period of time where one or more delta values is greater than angle
    yaws = eventual._yaws['delta']
    rolls = eventual._rolls['delta']
    pitches = eventual._pitches['delta']
    exper = eventual._experiment
    events = []
    maxSize = max(len(yaws), len(rolls), len(pitches))
    n = 0
    eventNumber = -1
    inEvent  =  False
    while n < maxSize:
        if inEvent:
            if abs(yaws[n]) > angle or abs(pitches[n]) > angle or abs(rolls[n]) > angle:

                events[eventNumber]['pitch'].append(pitches[n])
                events[eventNumber]['yaws'].append(yaws[n])
                events[eventNumber]['rolls'].append(rolls[n])
            else:
                 inEvent=False
        else:
            if abs(yaws[n]) > angle or abs(pitches[n]) > angle or abs(rolls[n]) > angle:
                inEvent=True
                eventNumber=eventNumber+1
                events.append({})
                events[eventNumber]['pitch'] = []
                events[eventNumber]['pitch'].append(pitches[n])
                events[eventNumber]['yaws'] = []
                events[eventNumber]['yaws'].append(yaws[n])
                events[eventNumber]['rolls'] = []
                events[eventNumber]['rolls'].append(rolls[n])
        n = n+1
    eventList=[]
    for item in events:
        pitch = item['pitch']
        yaw = item['yaws']
        roll = item['rolls']
        newEvent = Event(pitch, yaw, roll, exper)
        eventList.append(newEvent)
    return eventList



class Event(object):
    _duration = None
    _experiment = None
    _motion = None
    _speed = None
    _pitches = None
    _yaws = None
    _rolls = None
    name = None

    def __init__(self, pitch, yaw, roll, exper):
        """Pass a list of pitch, yaw, roll values, constructs an event from those lists"""
        self._pitches = pitch
        self._yaws = yaw
        self._rolls = roll
        self._experiment = exper
        self._duration = len(pitch)/10  #time is in 10th of a second, so this should just give us time in seconds
        if len(pitch) > 10:
            self._speed = velcro(self)
        else:
            self._speed= None
        self._motion = motionScore(self._yaws, self._pitches, self._rolls)

    def yaw(self, delta=True):
        return self._yaws

    def pitch(self, delta=True):
        return self._pitches

    def roll(self, delta=True):
        return self._rolls
