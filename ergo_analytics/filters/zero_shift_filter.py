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

__all__ = ["ZeroShiftFilter"]
__author__ = "Iterate Labs, Inc."
__version__ = "Alpha"

logger = logging.getLogger()


class ZeroShiftFilter(BaseTransformation):
    """
    Find and correct apparent zero-shifts in the data.
    """

    def __init__(self):
        super().__init__()

    def _initialize_params(self):
        super()._initialize_params()

    def apply(self, data=None):
        """
        Applies a quadrant filter to the incoming data.

        :param data:
        :param units: what are the units of the data? Degrees?
        :return:
        """
        super().apply(data=data)

        delta_columns = ['DeltaYaw', 'DeltaPitch', 'DeltaRoll']

        for col in delta_columns:
            data.loc[:, col] = self._adjust_for_zero_line(data=data.loc[:, col])

        data_transformed = data
        return self._update_data(data_transformed=data_transformed), {}

    def _adjust_for_zero_line(self, data=None):
        """
        Adjust the data by zero lines.
        """

        gradient = np.absolute(np.gradient(data))
        gradient = np.clip(gradient, a_min=0, a_max=None)

        q = 0
        percentile_to_use = np.abs(np.percentile(gradient, q=q))
        while percentile_to_use < 1e-10:
            q += 1  # 1 percentage-point at a time
            percentile_to_use = np.abs(np.percentile(gradient, q=q))

        print(f"Using the {q}th percentile to shift data up by before log.")

        gradient += percentile_to_use  # make sure we can take the log
        gradient = np.log(gradient)

        # shift happens(!) - but where?
        shift_indices = list(np.where(gradient > 0)[0])  # here

        if len(shift_indices) == 0:
            # nothing to shift/change
            return data

        # first mean - has to be gotten from calibration:
        first_mean = data.iloc[0]
        data.iloc[:shift_indices[0]] -= first_mean

        # TODO(JTK): This can be parallelized
        for j in range(len(shift_indices[1:])):
            the_new_zeroline = data[shift_indices[j]]
            data.iloc[shift_indices[j]:shift_indices[j + 1]] -= \
                the_new_zeroline

        # comes also from calibration:
        final_zero_line = data.iloc[-1]
        data.iloc[shift_indices[-1]:] = \
            data.iloc[shift_indices[-1]:] - final_zero_line

        return data
