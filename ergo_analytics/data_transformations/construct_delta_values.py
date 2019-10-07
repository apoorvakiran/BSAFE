# -*- coding: utf-8 -*-
"""
This transformation takes in data with yaw, pitch, and roll and
transforms this data into delta values. The delta refers to
values between the hand and wrist.

@ author Iterate Labs, Inc.
Copyright 2018-
"""

from . import BaseTransformation
import logging

__all__ = ["ConstructDeltaValues"]
__author__ = "Iterate Labs, Inc."
__version__ = "Alpha"

logger = logging.getLogger()


class ConstructDeltaValues(BaseTransformation):
    """
    Find the window of relevant data. For example, say the worker was not
    wearing the device for a while in the beginning or was setting up
    getting ready to start. Towards the end, maybe they did not turn off
    the device immediately.
    """

    def __init__(self, columns=None):
        """
        Construct the standard deviation filter.
        """
        super().__init__(columns=columns)

    def apply(self, data=None, data_format_code='4'):
        """
        Leverage standard deviation to find where the data starts and ends.

        If the worker is not using the device and/or not working the standard
        deviation should be smaller than if working.

        :param data: data for which delta angles are to be constructed.
        :param data_format_code: which format is the data in?
        """

        if data_format_code == '4':
            # already in delta-angle format
            return data, ('DeltaYaw', 'DeltaPitch', 'DeltaRoll')
        else:
            raise Exception("Implement me!")
