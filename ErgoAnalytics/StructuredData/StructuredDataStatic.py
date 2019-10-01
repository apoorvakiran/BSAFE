# -*- coding: utf-8 -*-
"""
Holds an Experiment object and everything related to it.

@ author Jesper Kristensen, Jacob Tyrrell
Copyright 2018
"""

__all__ = ["StructuredDataStatic"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import scipy
import numpy as np
import pandas as pd
import datetime
from scipy.interpolate import UnivariateSpline
from ..RawData import LoadDataFromLocalDisk
from . import BaseStructuredData
from .. import StandardDeviationFilter
from .. import QuadrantFilter


class StructuredDataStatic(BaseStructuredData):
    """
    This is a Structured Data class which is "static" meaning: It analyzes and
    loads data that is meant to represent a full set of cycles from start to
    finish (think: a full workday).
    """

    _time = None

    _yaw = None
    _pitch = None
    _roll = None

    _ax = None
    _ay = None
    _az = None
    _metrics = None

    _meta_data = None
    _data_format_code = None

    def __init__(self, path=None, destination=None, name=None, meta_data=None,
                 data_format_code='3'):
        """
        Construct an experiment class.
        :param path:
        :param destination:
        """
        super().__init__(name=name)

        self._data_format_code = data_format_code

        # this code is responsible for parsing the data from disk:
        dataloader = LoadDataFromLocalDisk()
        data = dataloader.get_data(path=path, destination=destination,
                                   data_format_code=self._data_format_code)
        # now run through pre-processing and validation:
        data = self._pre_process_data(data=data,
                                      names=dataloader.data_column_names)

        print("The data has successfully been loaded from disk and basic "
              "pre-processing has been performed.")
        print("Next step is to construct delta values "
              "(delta between wrist and hand).")

        self._time = pd.to_datetime(data['Date-Time'])

        self._yaw = dict()
        self._pitch = dict()
        self._roll = dict()
        #
        self._ax = dict()
        self._ay = dict()
        self._az = dict()
        #
        self._gx = dict()
        self._gy = dict()
        self._gz = dict()

        quadrant_filter = QuadrantFilter()

        if data_format_code not in ['4']:
            self._yaw['hand'] = data['Yaw[0](deg)'].astype(float)
            self._yaw['wrist'] = data['Yaw[1](deg)'].astype(float)
            self._yaw['delta'] = self._yaw['wrist'] - self._yaw['hand']
            #
            self._pitch['hand'] = data['Pitch[0](deg)'].astype(float)
            self._pitch['wrist'] = data['Pitch[1](deg)'].astype(float)
            self._pitch['delta'] = self._pitch['wrist'] - self._pitch['hand']
            #
            self._roll['hand'] = data['Roll[0](deg)'].astype(float)
            self._roll['wrist'] = data['Roll[1](deg)'].astype(float)
            self._roll['delta'] = self._roll['wrist'] - self._roll['hand']

            raise Exception("Needs fixing!")
            delta = self.construct_delta_values(yaw=self._yaw,
                                                pitch=self._pitch,
                                                roll=self._roll)

        else:
            # we only have delta values coming in:
            self._yaw['delta'] = quadrant_filter.apply(data['DeltaYaw'])
            self._pitch['delta'] = quadrant_filter.apply(data['DeltaPitch'])
            self._roll['delta'] = quadrant_filter.apply(data['DeltaRoll'])

        if data_format_code not in ['4']:
            self._ax['hand'] = data['ax[0](mg)'].astype(float)
            self._ax['wrist'] = data['ax[1](mg)'].astype(float)
            #
            self._ay['hand'] = data['ay[0](mg)'].astype(float)
            self._ay['wrist'] = data['ay[1](mg)'].astype(float)
            #
            self._az['hand'] = data['az[0](mg)'].astype(float)
            self._az['wrist'] = data['az[1](mg)'].astype(float)
        else:
            print("Raw acceleration data not included!")

        if data_format_code not in ['4']:
            self._gx['hand'] = data['gx[0](dps)'].astype(float)
            self._gx['wrist'] = data['gx[1](dps)'].astype(float)
            #
            self._gy['hand'] = data['gy[0](dps)'].astype(float)
            self._gy['wrist'] = data['gy[1](dps)'].astype(float)
            #
            self._gz['hand'] = data['gz[0](dps)'].astype(float)
            self._gz['wrist'] = data['gz[1](dps)'].astype(float)
        else:
            print("Gravitational data not included!")

        print("Delta values successfully constructed!")

        self._meta_data = meta_data

        std_filter = StandardDeviationFilter()
        std_filter.apply(structured_data=self)

    @property
    def meta_data(self):
        return self._meta_data

    @property
    def time(self):
        """
        The time associated with the measurements.
        :return:
        """
        return self._time

    def _scale(self, data=None):
        return (np.asarray(data) - 0) / (360 - 0)

    def _unscale(self, scaled_data=None):
        return np.asarray(scaled_data) * (360 - 0) + 0

    def scale_to_angles(self, data=None):
        deg1_unscaled = 1
        deg1_scaled = self._scale(data=[deg1_unscaled])

        return data / deg1_scaled

    def _transform(self, data=None):
        """
        Quadrant fix. Put all angles in [0, 90].
        # TODO: Might need improvement...
        :param data:
        :return:
        """
        return data

    def get_data(self, type='yaw', loc='hand', interpolate=True, delta=False):

        if type == 'yaw':
            data = self.yaw(loc=loc, interpolate=interpolate, delta=delta)
        elif type == 'pitch':
            data = self.pitch(loc=loc, delta=delta)
        elif type == 'roll':
            data = self.roll(loc=loc, delta=delta)
        else:
            raise Exception("This is an unknown data type '{}'!".format(type))

        return self._transform(data)

    def yaw(self, loc='hand', delta=False, interpolate=True):
        """
        Measures the yaw.
        :param loc:
        :return:
        """
        if delta or self._data_format_code in ['4']:
            return self._yaw['delta']

        return self._yaw[loc]

    def pitch(self, loc='hand', delta=False):
        """
        Measures the pitch.
        :param loc:
        :return:
        """
        if delta or self._data_format_code in ['4']:
            return self._pitch['delta']

        return self._pitch[loc]

    def roll(self, loc='hand', delta=False):
        """
        Measures the roll.
        :param loc:
        :return:
        """
        if delta or self._data_format_code in ['4']:
            return self._roll['delta']

        return self._roll[loc]

    def ax(self, loc='hand'):
        """
        Returns the linear accelerations along x.
        :param loc:
        :return:
        """
        if self._data_format_code in ['4']:
            return

        if loc in self._ax:
            return self._ax[loc]

    def ay(self, loc='hand'):
        """
        Returns the linear accelerations along y.
        :param loc:
        :return:
        """
        if self._data_format_code in ['4']:
            return

        if loc in self._ay:
            return self._ay[loc]

    def az(self, loc='hand'):
        """
        Returns the linear accelerations along z.
        :param loc:
        :return:
        """
        if self._data_format_code in ['4']:
            return

        if loc in self._az:
            return self._az[loc] / 1000 - 1  # subtract gravity

    def gx(self, loc='hand'):
        """
        Angular velocity around x-axis.
        :param loc:
        :return:
        """
        if self._data_format_code in ['4']:
            return

        if loc in self._gx:
            return self._gx[loc]

    def gy(self, loc='hand'):
        """
        Angular velocity around y-axis.
        :param loc:
        :return:
        """
        if self._data_format_code in ['4']:
            return

        if loc in self._gy:
            return self._gy[loc]

    def gz(self, loc='hand'):
        """
        Angular velocity around z-axis.
        :param loc:
        :return:
        """
        if self._data_format_code in ['4']:
            return

        if loc in self._gz:
            return self._gz[loc]

    def angular_acc_x(self, loc='hand'):
        """
        Angular acceleration around x-axis.

        :param loc:
        :return:
        """
        # need to obtain this as derivative in time from the gyroscope data

        x = self.time
        w = self.gx(loc=loc)  # degrees per second (DPS) (angular velocity)

        x_conv = (pd.to_datetime(x) -
                  datetime.datetime(1970, 1, 1)).apply(lambda x: x.total_seconds())

        w_interp = UnivariateSpline(x_conv, w)  # w(t) --> velocity

        alpha_interp = w_interp.derivative(n=1)  # alpha = dw(t)/dt --> angular acceleration

        return alpha_interp(x_conv)

    def truncate(self, lowEnd, highEnd):
        """
        Going to truncate to just the low:high values in the data ranges.
        """
        for key in self._yaw:
            self._yaw[key] = self._yaw[key][lowEnd:highEnd]

        for key in self._pitch:
            self._pitch[key] = self._pitch[key][lowEnd:highEnd]

        for key in self._roll:
            self._roll[key] = self._roll[key][lowEnd:highEnd]

        for key in self._ax:
            self._ax[key] = self._ax[key][lowEnd:highEnd]

        for key in self._ay:
            self._ay[key] = self._ay[key][lowEnd:highEnd]

        for key in self._az:
            self._az[key] = self._az[key][lowEnd:highEnd]

        self._time = self._time[lowEnd:highEnd]

        return (self)

    def filter_data_on_standard_deviation(self):
        """
        Toss an experiment at this, it will return a truncated experiment
        Discards values until a point where standard deviation has been higher for 30 seconds
        than it was in the first 10 seconds, for both pitch and yaw.
        Does the same for the end of the list, discarding the end values.
        """
        yawDel = self.get_data(type='yaw', delta=True)
        startYawDev = scipy.std(yawDel[0:100])
        pitchDel = self.get_data(type='pitch', delta=True)
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
        startPoint = n - 200
        n = -1
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
        endPoint = n + 200
        return (self.truncate(startPoint, endPoint))

    def construct_delta_values(self, yaw=None, pitch=None, roll=None):
        """
        Construct delta values.

        :param experiment:
        :return:
        """
        handy = np.array(self.yaw(loc='hand')) - np.mean(self.yaw(loc='hand'))
        wristy = np.array(self.yaw(loc='wrist')) - np.mean(self.yaw(loc='wrist'))
        handp = np.array(self.pitch(loc='hand')) - np.mean(self.pitch(loc='hand'))
        wristp = np.array(self.pitch(loc='wrist')) - np.mean(self.pitch(loc='wrist'))
        handr = np.array(self.roll(loc='hand')) - np.mean(self.roll(loc='hand'))
        wristr = np.array(self.roll(loc='wrist')) - np.mean(self.roll(loc='wrist'))

        newHandy = self.center_values(list_uncentered=handy)
        newWristy = self.center_values(list_uncentered=wristy)
        newHandp = self.center_values(list_uncentered=handp)
        newWristp = self.center_values(list_uncentered=wristp)
        newHandr = self.center_values(list_uncentered=handr)
        newWristr = self.center_values(list_uncentered=wristr)

        yawz = dict()
        yawz['hand'] = self.quadrant_fix(newHandy)
        yawz['wrist'] = self.quadrant_fix(newWristy)
        yawz['delta'] = self.quadrant_fix(newWristy - newHandy)
        pitchz = dict()
        pitchz['hand'] = self.quadrant_fix(newHandp)
        pitchz['wrist'] = self.quadrant_fix(newWristp)
        pitchz['delta'] = self.quadrant_fix(newWristp - newHandp)
        rollz = dict()
        rollz['hand'] = self.quadrant_fix(newHandr)
        rollz['wrist'] = self.quadrant_fix(newWristr)
        rollz['delta'] = self.quadrant_fix(newWristr - newHandr)

        return yawz, pitchz, rollz

    def center_values(self, list_uncentered=None):
        """
        Takes a list of angle data and returns a list
        of data centered at zero.
        """
        newList = list_uncentered - np.mean(list_uncentered)
        return newList
