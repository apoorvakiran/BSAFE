# -*- coding: utf-8 -*-
"""
This transformation takes in raw data that has been transformed and
filtered and turns it into structured data.

@ author Jesper Kristensen
Copyright 2018- Iterate Labs, Inc.
"""

__all__ = ["CreateStructuredData"]
__author__ = "Iterate Labs, Inc."
__version__ = "Alpha"

from . import BaseTransformation
from ..Data_Structured import StructuredDataStatic
import logging

logger = logging.getLogger()


class CreateStructuredData(BaseTransformation):
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

        return StructuredDataStatic(data=data,
                                    data_format_code=data_format_code)
