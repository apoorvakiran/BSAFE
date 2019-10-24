# -*- coding: utf-8 -*-
"""
This filter ensure that angles are within the expected and
correct quadrants of the unit circle.

@ author Iterate Labs, Inc.
Copyright 2018-
"""

import logging
import numpy as np
from . import BaseTransformation
from .. import rad_to_deg

__all__ = ["QuadrantFilter"]
__author__ = "Iterate Labs, Inc."
__version__ = "Alpha"

logger = logging.getLogger()


class QuadrantFilter(BaseTransformation):
    """
    Applies the quadrant filter to structured data arising at
    times due primarily to Gimball lock.
    """

    def __init__(self, columns=None):
        super().__init__(columns=columns)

    def _initialize_params(self):
        self._params = dict(units='deg')

    def apply(self, data=None):
        """
        Applies a quadrant filter to the incoming data.

        :param data:
        :param units: what are the units of the data? Degrees?
        :return:
        """
        super().apply(data=data)

        units = self._params['units']

        if not units or units not in ['deg', 'rad']:
            raise Exception("Units '{}' not understood!\n"
                            "Valid options: 'deg', 'rad'".format(units))

        this_data = data.loc[:, self._columns]
        if units == 'rad':
            this_data = rad_to_deg(this_data)

        # first get indices beyond thresholds:
        ind_above = this_data > 180
        ind_below = this_data < -180

        # then apply the 180-degree correction:
        this_data[ind_above] -= 360
        this_data[ind_below] += 360

        # finally limit all data to [-90, 90]:
        data_transformed = np.clip(this_data, a_min=-90, a_max=90)

        return self._update_data(data_transformed=data_transformed), {}
