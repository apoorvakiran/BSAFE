# -*- coding: utf-8 -*-
"""
Handles streaming data.

@ author Jesper Kristensen and Jacob Tyrrell
Copyright Iterate Labs, Inc. 2018+
"""

__all__ = ["StructuredDataStreaming"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import logging
import numpy as np
import pandas as pd
import datetime
from scipy.interpolate import UnivariateSpline
from ..RawData import LoadElasticSearch
from . import BaseStructuredData
from .. import QuadrantFilter

logger = logging.getLogger()


class StructuredDataStreaming(BaseStructuredData):
    """
    This is a Structured Data class which is "streaming" meaning: It analyzes
    and loads data streaming in from the glove in real time. This is opposed
    to the "static" version which assumes that all data is collected from
    start to finish.
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

    def __init__(self, streaming_source='elastic_search',
                 streaming_settings=None, name=None, meta_data=None,
                 data_format_code='2'):
        """
        Construct an experiment class.
        :param path:
        :param destination:
        """
        super().__init__(name=name)

        # where is the data streaming from?
        if streaming_source == 'elastic_search':

            if not streaming_settings:
                raise Exception("Please provide settings for "
                                "the data streaming code!")

            dataloader = LoadElasticSearch()
            data = dataloader.retrieve_data(data_format_code=data_format_code,
                                            **streaming_settings)

        else:
            raise NotImplementedError("Implement the streaming "
                                      "source '{}'!".format(streaming_source))

        if data is None:
            # no data was loaded!
            logger.info("No data was loaded in the streaming process!")
            return

        self._time = pd.to_datetime(data['Date-Time'])

        self._yaw = dict()
        self._pitch = dict()
        self._roll = dict()

        quadrant_filter = None
        if data_format_code == '3':
            self._yaw['hand'] = data['yaw[0]'].astype(float)
            self._yaw['wrist'] = data['yaw[1]'].astype(float)
            self._yaw['delta'] = self._yaw['wrist'] - self._yaw['hand']
        elif data_format_code == '4':
            quadrant_filter = QuadrantFilter()
            self._yaw['delta'] = quadrant_filter.apply(data['DeltaYaw'])
        else:
            self._yaw['hand'] = data['Yaw[0](deg)'].astype(float)
            self._yaw['wrist'] = data['Yaw[1](deg)'].astype(float)
            self._yaw['delta'] = self._yaw['wrist'] - self._yaw['hand']

        if data_format_code == '3':
            self._pitch['hand'] = data['pitch[0]'].astype(float)
            self._pitch['wrist'] = data['pitch[1]'].astype(float)
            self._pitch['delta'] = self._pitch['wrist'] - self._pitch['hand']
        elif data_format_code == '4':
            self._pitch['delta'] = quadrant_filter.apply(data['DeltaPitch'])
        else:
            self._pitch['hand'] = data['Pitch[0](deg)'].astype(float)
            self._pitch['wrist'] = data['Pitch[1](deg)'].astype(float)
            self._pitch['delta'] = self._pitch['wrist'] - self._pitch['hand']

        if data_format_code == '3':
            self._roll['hand'] = data['roll[0]'].astype(float)
            self._roll['wrist'] = data['roll[1]'].astype(float)
            self._roll['delta'] = self._roll['wrist'] - self._roll['hand']
        elif data_format_code == '4':
            self._roll['delta'] = quadrant_filter.apply(data['DeltaRoll'])
        else:
            self._roll['hand'] = data['Roll[0](deg)'].astype(float)
            self._roll['wrist'] = data['Roll[1](deg)'].astype(float)
            self._roll['delta'] = self._roll['wrist'] - self._roll['hand']

        if data_format_code not in ['4']:

            delta = self.construct_delta_values(yaw=self._yaw,
                                                pitch=self._pitch,
                                                roll=self._roll)

            self._yaw['delta'] = delta['yaw']['delta']
            self._pitch['delta'] = delta['pitch']['delta']
            self._roll['delta'] = delta['roll']['delta']

            self._yaw = delta[0]
            self._pitch = delta[1]
            self._roll = delta[2]

            self._ax = dict()
            self._ay = dict()
            self._az = dict()
            #
            if 'ax[0](mg)' in data:
                self._ax['hand'] = data['ax[0](mg)'].astype(float)
                self._ax['wrist'] = data['ax[1](mg)'].astype(float)
                #
                self._ay['hand'] = data['ay[0](mg)'].astype(float)
                self._ay['wrist'] = data['ay[1](mg)'].astype(float)
                #
                self._az['hand'] = data['az[0](mg)'].astype(float)
                self._az['wrist'] = data['az[1](mg)'].astype(float)
            else:
                logger.info("Raw acceleration data not included!")

            self._gx = dict()
            self._gy = dict()
            self._gz = dict()
            if "gx[0](dps)" in data:

                self._gx['hand'] = data['gx[0](dps)'].astype(float)
                self._gx['wrist'] = data['gx[1](dps)'].astype(float)
                #
                self._gy['hand'] = data['gy[0](dps)'].astype(float)
                self._gy['wrist'] = data['gy[1](dps)'].astype(float)
                #
                self._gz['hand'] = data['gz[0](dps)'].astype(float)
                self._gz['wrist'] = data['gz[1](dps)'].astype(float)

        import pdb
        pdb.set_trace()
        self._meta_data = meta_data

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
        if delta:
            return self._yaw['delta']

        return self._yaw[loc]

    def pitch(self, loc='hand', delta=False):
        """
        Measures the pitch.
        :param loc:
        :return:
        """
        if delta:
            return self._pitch['delta']

        return self._pitch[loc]

    def roll(self, loc='hand', delta=False):
        """
        Measures the roll.
        :param loc:
        :return:
        """
        if delta:
            return self._roll['delta']

        return self._roll[loc]

    def ax(self, loc='hand'):
        """
        Returns the linear accelerations along x.
        :param loc:
        :return:
        """
        if loc in self._ax:
            return self._ax[loc]

    def ay(self, loc='hand'):
        """
        Returns the linear accelerations along y.
        :param loc:
        :return:
        """
        if loc in self._ay:
            return self._ay[loc]

    def az(self, loc='hand'):
        """
        Returns the linear accelerations along z.
        :param loc:
        :return:
        """
        if loc in self._az:
            return self._az[loc] / 1000 - 1  # subtract gravity

    def gx(self, loc='hand'):
        """
        Angular velocity around x-axis.
        :param loc:
        :return:
        """
        if loc in self._gx:
            return self._gx[loc]

    def gy(self, loc='hand'):
        """
        Angular velocity around y-axis.
        :param loc:
        :return:
        """
        if loc in self._gy:
            return self._gy[loc]

    def gz(self, loc='hand'):
        """
        Angular velocity around z-axis.
        :param loc:
        :return:
        """
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

    def construct_delta_values(self, yaw=None, pitch=None, roll=None):
        """
        Construct delta values.

        :param experiment:
        :return:
        """
        # yaw
        handy = np.array(yaw['hand']) - np.mean(yaw['hand'])
        wristy = np.array(yaw['wrist']) - np.mean(yaw['wrist'])
        # pitch
        handp = np.array(pitch['hand']) - np.mean(pitch['hand'])
        wristp = np.array(pitch['wrist']) - np.mean(pitch['wrist'])
        # roll
        handr = np.array(roll['hand']) - np.mean(roll['hand'])
        wristr = np.array(roll['wrist']) - np.mean(roll['wrist'])

        newHandy = self.center_values(data_uncentered=handy)
        newWristy = self.center_values(data_uncentered=wristy)
        newHandp = self.center_values(data_uncentered=handp)
        newWristp = self.center_values(data_uncentered=wristp)
        newHandr = self.center_values(data_uncentered=handr)
        newWristr = self.center_values(data_uncentered=wristr)

        quadrant_filter = QuadrantFilter()

        yawz = dict()
        yawz['hand'] = quadrant_filter.apply(data=newHandy)
        yawz['wrist'] = quadrant_filter.apply(data=newWristy)
        yawz['delta'] = quadrant_filter.apply(data=newWristy - newHandy)

        pitchz = dict()
        pitchz['hand'] = quadrant_filter.apply(data=newHandp)
        pitchz['wrist'] = quadrant_filter.apply(data=newWristp)
        pitchz['delta'] = quadrant_filter.apply(data=newWristp - newHandp)

        rollz = dict()
        rollz['hand'] = quadrant_filter.apply(data=newHandr)
        rollz['wrist'] = quadrant_filter.apply(data=newWristr)
        rollz['delta'] = quadrant_filter.apply(data=newWristr - newHandr)

        return {'yaw': yawz, 'pitch': pitchz, 'roll': rollz}

    def center_values(self, data_uncentered=None):
        """
        Takes a list of angle data and returns a list
        of data centered at zero.
        """
        newList = data_uncentered - np.mean(data_uncentered)
        return newList
