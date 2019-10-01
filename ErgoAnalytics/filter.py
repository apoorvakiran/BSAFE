# -*- coding: utf-8 -*-
"""
Defines filters that can be applied to data.

@ author Iterate Labs, Inc.
Copyright 2018-
"""

import logging
import scipy
import numpy as np

__all__ = ["StandardDeviationFilter", "QuadrantFilter"]
__author__ = "Iterate Labs, Inc."
__version__ = "Alpha"

logger = logging.getLogger()


class BaseFilter(object):
    """
    Applies a filter to data.
    """
    
    def __init__(self):
        pass

    def apply(self, structured_data=None):
        raise NotImplementedError("Implement me!")


class StandardDeviationFilter(BaseFilter):
    """
    Standard deviation filter: Discard data with high standard deviation.
    """

    def apply(self, structured_data=None):
        """
        Toss an experiment at this, it will return a truncated experiment
        Discards values until a point where standard deviation has been higher for 30 seconds
        than it was in the first 10 seconds, for both pitch and yaw.
        Does the same for the end of the list, discarding the end values.
        """

        yawDel = structured_data.get_data(type='yaw', delta=True)
        startYawDev = scipy.std(yawDel[0:100])
        pitchDel = structured_data.get_data(type='pitch', delta=True)
        startPitchDev = scipy.std(pitchDel[0:100])

        n = 0
        lastThreeYaw = [0, 0, 0]
        lastThreePitch = [0, 0, 0]
        while (startYawDev >= lastThreeYaw[0] or
                startYawDev >= lastThreeYaw[1] or
                startYawDev >= lastThreeYaw[2] or
                startPitchDev >= lastThreePitch[0] or
                startPitchDev >= lastThreePitch[1] or
                startPitchDev >= lastThreePitch[2]):
            highEnd = n + 99
            lastThreeYaw.pop(0)
            lastThreePitch.pop(0)
            lastThreeYaw.append(scipy.std(yawDel[n:highEnd]))
            lastThreePitch.append(scipy.std(pitchDel[n:highEnd]))
            n = n + 100
        startPoint = max(0, n - 200)

        n = len(yawDel)
        lastThreeYaw = [0, 0, 0]
        lastThreePitch = [0, 0, 0]
        while (startYawDev >= lastThreeYaw[0] or
                startYawDev >= lastThreeYaw[1] or
                startYawDev >= lastThreeYaw[2] or
                startPitchDev >= lastThreePitch[0] or
                startPitchDev >= lastThreePitch[1] or
                startPitchDev >= lastThreePitch[2]):
            lowEnd = n - 99
            lastThreeYaw.pop(0)
            lastThreePitch.pop(0)
            lastThreeYaw.append(scipy.std(yawDel[lowEnd:n]))
            lastThreePitch.append(scipy.std(pitchDel[lowEnd:n]))
            n = n - 100
        endPoint = min(n + 200, len(yawDel))

        # alter data in-place:
        self.truncate(structured_data=structured_data,
                      lo=startPoint, hi=endPoint)

    def truncate(self, structured_data=None, lo=None, hi=None):
        """
        Going to truncate to just the low:high values in the data ranges.
        """
        for key in structured_data._yaw:
            structured_data._yaw[key] = structured_data._yaw[key][lo:hi]

        for key in structured_data._pitch:
            structured_data._pitch[key] = structured_data._pitch[key][lo:hi]

        for key in structured_data._roll:
            structured_data._roll[key] = structured_data._roll[key][lo:hi]

        for key in structured_data._ax:
            structured_data._ax[key] = structured_data._ax[key][lo:hi]

        for key in structured_data._ay:
            structured_data._ay[key] = structured_data._ay[key][lo:hi]

        for key in structured_data._az:
            structured_data._az[key] = structured_data._az[key][lo:hi]

        structured_data._time = structured_data._time[lo:hi]


class QuadrantFilter(BaseFilter):
    """
    Applies the quadrant filter to structured data arising at
    times due primarily to Gimball lock.
    """

    def __init__(self):

        super().__init__()

    def apply(self, data=None):

        data = data.astype(float)

        # first get indices beyond thresholds:
        ind_above = data > 180
        ind_below = data < -180

        # then apply the 180-degree correction:
        data[ind_above] -= 360
        data[ind_below] += 360

        return np.clip(data, a_min=-90, a_max=90)  # clip to range [-90, 90]
