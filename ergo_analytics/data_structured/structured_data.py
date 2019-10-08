# -*- coding: utf-8 -*-
"""
Holds a Structured Data object and everything related to it.

@ author Jesper Kristensen, Jacob Tyrrell
Copyright 2018
"""

__all__ = ["StructuredData"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import pandas as pd
from . import BaseStructuredData
import logging

logger = logging.getLogger()


class StructuredData(BaseStructuredData):
    """
    This is a Structured Data class which is "static" meaning: It analyzes and
    loads data that is meant to represent a full set of cycles from start to
    finish (think: a full workday).
    """

    _time = None
    _meta_data = None
    _data_format_code = None
    _delta_yaw = None
    _delta_pitch = None
    _delta_roll = None

    def __init__(self, data=None, meta_data=None, data_format_code=None):
        """
        Construct a structured data object holding incoming
        data in an organized way.

        :param data:
        :param destination:
        """
        super().__init__()

        self._data_format_code = data_format_code

        self._time = pd.to_datetime(data['Date-Time'])

        if self._data_format_code == '4':
            self._yaw = dict()
            self._yaw['delta'] = data['DeltaYaw']
            #
            self._pitch = dict()
            self._pitch['delta'] = data['DeltaPitch']
            #
            self._roll = dict()
            self._roll['delta'] = data['DeltaRoll']

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

    def get_data(self, type='yaw', loc='delta'):
        """
        Returns data collected from the device.

        :param type:
        :param loc:
        :return:
        """
        if type == 'yaw':
            data = self.yaw(loc=loc)
        elif type == 'pitch':
            data = self.pitch(loc=loc)
        elif type == 'roll':
            data = self.roll(loc=loc)
        else:
            msg = "This is an unknown data type '{}'!".format(type)
            logger.exception(msg)
            raise Exception(msg)

        return data

    def yaw(self, loc='delta'):
        """
        Returns the yaw data.

        :param loc:
        :return:
        """
        return self._yaw[loc]

    def pitch(self, loc='delta'):
        """
        Returns the pitch data.

        :param loc:
        :return:
        """
        return self._pitch[loc]

    def roll(self, loc='delta'):
        """
        Returns the roll data.

        :param loc:
        :return:
        """
        return self._roll[loc]
