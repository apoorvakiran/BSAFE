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

    def __init__(self):
        """
        Construct the standard deviation filter.
        """
        super().__init__()

    def _initialize_params(self):
        super()._initialize_params()

    def apply(self, data=None, **kwargs):
        """
        Leverage standard deviation to find where the data starts and ends.

        If the worker is not using the device and/or not working the standard
        deviation should be smaller than if working.

        :param data: data for which delta angles are to be constructed.
        :param data_format_code: which format is the data in?
        """
        super().apply(data=data, **kwargs)

        params = self._params
        if params['data_format_code'] in {'1', '5'}:
            # need to construct delta's
            data['DeltaYaw'] = data['Yaw[1](deg)'] - data['Yaw[0](deg)']
            data['DeltaPitch'] = data['Pitch[1](deg)'] - data['Pitch[0](deg)']
            data['DeltaRoll'] = data['Roll[1](deg)'] - data['Roll[0](deg)']
        elif params['data_format_code'] == '4':
            # already in delta-angle format
            pass
        else:
            raise Exception("Implement me!")

        data_to_return = self._update_data(data_transformed=data,
                                           columns_operated_on=['DeltaYaw',
                                                                'DeltaPitch',
                                                                'DeltaRoll'])

        return data_to_return, \
               {'added': ['DeltaYaw', 'DeltaPitch', 'DeltaRoll']}
