# -*- coding: utf-8 -*-
"""
Holds an Experiment object and everything related to it.

@ author Jesper Kristensen, Jacob Tyrrell
Copyright 2018
"""

__all__ = ["StructuredDataStreaming"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import numpy as np
import pandas as pd
import datetime
from scipy.interpolate import UnivariateSpline
from Analytics import LoadElasticSearch
from . import BaseStructuredData


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
                 data_format_code='3'):
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
            data = dataloader.retrieve_data(**streaming_settings)
            
        else:
            raise NotImplementedError("Implement the streaming "
                                      "source '{}'!".format(streaming_source))

        if data is None:
            # no data was loaded!
            print("No data was loaded in the streaming process!")
            return

        self._time = pd.to_datetime(data['Date-Time'])

        self._yaw = dict()
        self._pitch = dict()
        self._roll = dict()

        if data_format_code == '3':
            self._yaw['hand'] = data['yaw[0]'].astype(float)
            self._yaw['wrist'] = data['yaw[1]'].astype(float)
        else:
            self._yaw['hand'] = data['Yaw[0](deg)'].astype(float)
            self._yaw['wrist'] = data['Yaw[1](deg)'].astype(float)
        self._yaw['delta'] = self._yaw['wrist'] - self._yaw['hand']

        if data_format_code == '3':
            self._pitch['hand'] = data['pitch[0]'].astype(float)
            self._pitch['wrist'] = data['pitch[1]'].astype(float)
        else:
            self._pitch['hand'] = data['Pitch[0](deg)'].astype(float)
            self._pitch['wrist'] = data['Pitch[1](deg)'].astype(float)
        self._pitch['delta'] = self._pitch['wrist'] - self._pitch['hand']

        if data_format_code == '3':
            self._roll['hand'] = data['roll[0]'].astype(float)
            self._roll['wrist'] = data['roll[1]'].astype(float)
        else:
            self._roll['hand'] = data['Roll[0](deg)'].astype(float)
            self._roll['wrist'] = data['Roll[1](deg)'].astype(float)
        self._roll['delta'] = self._roll['wrist'] - self._roll['hand']

        try:
            delta = self.construct_delta_values()
            print("Delta values successfully constructed!")
        except Exception:
            print("There was an error processing/creating the 'delta' "
                  "values of the data!")
            raise Exception("There was an error in creating delta values!")

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
            print("Raw acceleration data not included!")

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
        # return np.degrees(np.arcsin(np.sin(np.radians(data))))

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
        # raw_data = self._yaw[loc].values.reshape(-1, 1)
        #
        # # standardize
        # raw_data_scaled = self._scale(raw_data)
        #
        # raw_10deg = 10
        # raw_1deg = 1
        #
        # scaled_10deg = self._scale([raw_10deg])
        # scaled_1deg = self._scale([raw_1deg])
        #
        # x = np.arange(len(raw_data_scaled))
        #
        # yaw_data = savgol_filter(raw_data_scaled.reshape(1, -1), 11, 4)
        #
        # df = pd.DataFrame(data=np.vstack([x, yaw_data]).T, columns=['Time', "Yaw"])
        # df = df.rolling(11).mean()
        #
        # level_zero = np.mean(df.loc[:280, 'Yaw'])
        # df.loc[:, 'Yaw'] = df.loc[:, 'Yaw'] - level_zero
        #
        # plt.figure()
        # plt.subplot(211)
        # plt.title("Raw Data")
        # plt.plot(x, raw_data, 'bx', zorder=1)
        # plt.axvline(280)
        # plt.grid()
        #
        # plt.subplot(212)
        # plt.title("Processed data")
        # plt.plot(df['Time'] / 10, self.scale_to_angles(data=df['Yaw']), 'r-', zorder=2)
        # plt.axhline(10, linestyle='--', color='k')
        # plt.axhline(20, linestyle='--', color='k')
        # plt.axhline(30, linestyle='--', color='k')
        # plt.xlabel("Time (s)")
        # plt.ylabel("Angle (deg)")
        # plt.grid()
        # plt.tight_layout()
        #
        # plt.figure()
        #
        # max_y_level = self.scale_to_angles(data=df['Yaw']).max()
        #
        # # plt.subplot(211)
        # # plt.title("Processed data")
        # # plt.plot(df['Time'] / 10, self.scale_to_angles(data=df['Yaw']), 'r-', zorder=2)
        # # plt.axhline(10, linestyle='--', color='k')
        # # plt.axhline(20, linestyle='--', color='k')
        # # plt.axhline(30, linestyle='--', color='k')
        # # plt.xlabel("Time (s)")
        # # plt.ylabel("Angle (deg)")
        # # plt.grid()
        #
        # # plt.subplot(212)
        # x = df['Time'] / 10
        # rula_threshold = 15
        # plt.plot(x, self.scale_to_angles(data=df['Yaw']), 'r-', zorder=2)
        # # plt.axhline(rula_threshold, linestyle='--', color='k')
        #
        # plt.axhspan(0, rula_threshold * 0.8, color='g', alpha=0.2)
        # plt.axhspan(rula_threshold * 0.8, rula_threshold, color='y', alpha=0.2)
        # plt.axhspan(rula_threshold, max_y_level, color='r', alpha=0.2)
        #
        # plt.xlabel("Time (s)")
        # plt.ylabel("Angle (deg)")
        # plt.grid()
        # plt.tight_layout()
        #
        # plt.show()

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

        # plt.figure()
        # plt.plot(x, w, 'r--')
        # plt.plot(x, w_interp(x_conv), 'bx')
        # plt.show()

        return alpha_interp(x_conv)

    # def quadCorrect(self, swing = 180):
    # """
    # Take an experiment object and reduce large swings in angle from measurement to measurement.
    # swing is the maximum value by which an angle will be allowed to change in one timestep
    # """
    # start by grabbing the length of the array
    # lend=len(self._time)
    # dictions=[self._yaw, self._pitch, self._roll]
    # #these three dictionaries need to be checked and updated on multiple values
    # n=1
    # #Switching to np array objects, easier to perform updates here.
    # self._yaw['hand']=np.array(self._yaw['hand'])
    # self._yaw['wrist']=np.array(self._yaw['wrist'])
    # self._yaw['delta']=np.array(self._yaw['delta'])
    # self._pitch['hand']=np.array(self._pitch['hand'])
    # self._pitch['wrist']=np.array(self._pitch['wrist'])
    # self._pitch['delta']=np.array(self._pitch['delta'])
    # self._roll['hand']=np.array(self._roll['hand'])
    # self._roll['wrist']=np.array(self._roll['wrist'])
    # self._roll['delta']=np.array(self._roll['delta'])
    # while (n<lend) :
    #  for set in dictions:
    #    changed=False #set to true if changes are made, then update delta.
    #    #print(set.keys())
    #    handSwing=abs(set['hand'][n]-set['hand'][n-1])
    #    #print(handSwing)
    #    wristSwing=abs(set['wrist'][n]-set['wrist'][n-1])
    #    if (handSwing >swing):
    #      #print(set['hand'][n-1])
    #      set['hand'][n]=set['hand'][n-1] #sets it to the previous value (swing of 0)
    #      #print(set['hand'][n])
    #      changed=True
    #    if (wristSwing>swing):
    #      set['wrist'][n]=set['wrist'][n-1]
    #      changed=True
    #    if changed:
    #      set['delta'][n]=set['wrist'][n]-set['hand'][n]
    #    #print('Updated quadrant for value ' + str(n))
    #    #print(handSwing)
    #    #print(wristSwing)
    #  n=n+1
    ##Transferring between Series and np.array objects, back to a Series.
    # self._yaw['hand']=pd.Series(self._yaw['hand'])
    # self._yaw['wrist']=pd.Series(self._yaw['wrist'])
    # self._yaw['delta']=pd.Series(self._yaw['delta'])
    # self._pitch['hand']=pd.Series(self._pitch['hand'])
    # self._pitch['wrist']=pd.Series(self._pitch['wrist'])
    # self._pitch['delta']=pd.Series(self._pitch['delta'])
    # self._roll['hand']=pd.Series(self._roll['hand'])
    # self._roll['wrist']=pd.Series(self._roll['wrist'])
    # self._roll['delta']=pd.Series(self._roll['delta'])
    # return(self)

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

    def construct_delta_values(self):
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

        yawz = {}
        yawz['hand'] = self.quadrant_fix(newHandy)
        yawz['wrist'] = self.quadrant_fix(newWristy)
        yawz['delta'] = self.quadrant_fix(newWristy - newHandy)
        pitchz = {}
        pitchz['hand'] = self.quadrant_fix(newHandp)
        pitchz['wrist'] = self.quadrant_fix(newWristp)
        pitchz['delta'] = self.quadrant_fix(newWristp - newHandp)
        rollz = {}
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

    def quadrant_fix(self, list_data=None):
        # print(listy)
        n = 0
        try:
            while n < len(list_data):
                if list_data[n] > 180:
                    list_data[n] = list_data[n] - 360
                if list_data[n] < -180:
                    list_data[n] = list_data[n] + 360
                n = n + 1
        except:
            print("Failure on processing quadrant correction/fix for ")
            print(list_data)
        return self.quadzTwo(list_data)

    def quadzTwo(self, list_data=None):

        n = 0
        try:
            while n < len(list_data):
                if list_data[n] > 90:
                    if n > 0:
                        list_data[n] = list_data[n - 1]
                    else:
                        list_data[n] = 90
                if list_data[n] < -90:
                    if n > 0:
                        list_data[n] = list_data[n - 1]
                    else:
                        list_data[n] = -90
                n = n + 1
        except:
            print("Failure in Quadztwo")

        return list_data
