# -*- coding: utf-8 -*-
"""Holds a Structured Data object and everything related to it.

@ author Jesper Kristensen
Copyright 2018- Iterate Labs, Inc.
All Rights Reserved.
"""

__all__ = ["StructuredData"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import numpy as np
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
    _data_matrix = None
    _data_format_code = None
    _delta_yaw = None
    _delta_pitch = None
    _delta_roll = None
    _number_of_points = None

    def __init__(self, data=None, data_format_code=None):
        """
        Construct a structured data object holding incoming
        data in an organized way.

        :param data:
        :param destination:
        """
        super().__init__()

        self._check_data(data=data)

        self._data_format_code = data_format_code

        try:
            self._time = pd.to_datetime(data["Date-Time"])
        except Exception:
            self._time = np.arange(len(data))

        self._yaw = dict()
        self._yaw["delta"] = data["DeltaYaw"]
        #
        self._pitch = dict()
        self._pitch["delta"] = data["DeltaPitch"]
        #
        self._roll = dict()
        self._roll["delta"] = data["DeltaRoll"]

        self._number_of_points = len(data)

        self._data_matrix = data

    @property
    def data_matrix(self):
        """Return the data matrix as originally came in."""
        return self._data_matrix

    @staticmethod
    def _check_data(data=None):
        """
        Checks that the incoming data is in the format of the Structured data.
        """
        if (
            "DeltaYaw" not in data
            or "DeltaPitch" not in data
            or "DeltaRoll" not in data
        ):
            msg = (
                "The incoming data is not in expected format!\n"
                "Please make sure to create all delta angles!"
            )
            raise Exception(msg)

    @property
    def number_of_points(self):
        return self._number_of_points

    @property
    def time(self):
        """
        The time associated with the measurements.
        :return:
        """
        return self._time

    def get_first_index(self):
        """Return the first index of the data.

        :return:
        """
        return self.get_data(type="yaw", loc="delta").index[0]

    def get_last_index(self):
        """Return the last index of the data.

        :return:
        """
        return self.get_data(type="yaw", loc="delta").index[-1]

    def get_data(self, type="yaw", loc="delta"):
        """
        Returns data collected from the device.

        :param type:
        :param loc:
        :return:
        """
        if type == "yaw":
            data = self.yaw(loc=loc)
        elif type == "pitch":
            data = self.pitch(loc=loc)
        elif type == "roll":
            data = self.roll(loc=loc)
        else:
            msg = "This is an unknown data type '{}'!".format(type)
            logger.exception(msg)
            raise Exception(msg)

        return data

    def yaw(self, loc="delta"):
        """
        Returns the yaw data.

        :param loc:
        :return:
        """
        return self._yaw[loc]

    def pitch(self, loc="delta"):
        """
        Returns the pitch data.

        :param loc:
        :return:
        """
        return self._pitch[loc]

    def roll(self, loc="delta"):
        """
        Returns the roll data.

        :param loc:
        :return:
        """
        return self._roll[loc]
