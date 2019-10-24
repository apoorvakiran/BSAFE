# -*- coding: utf-8 -*-
"""
This filter can help analyze and process data based on its
standard deviation.

@ author Jesper Kristensen & Jacob Tyrrell
Copyright 2018- Iterate Labs, Inc.
"""

from constants import SAMPLING_RATE
from constants import DATA_FORMAT_CODES
from . import BaseTransformation
import logging

__all__ = ["WindowOfRelevantDataFilter"]
__author__ = "Iterate Labs, Inc."
__version__ = "Alpha"

logger = logging.getLogger()


class WindowOfRelevantDataFilter(BaseTransformation):
    """
    Find the window/region of relevant data. For example,
    say the worker was not wearing the device for a while in the beginning or
    was setting up getting ready to start. Towards the end, maybe they
    did not turn off the device immediately.
    """

    _columns = None  # which columns to apply this filter to?

    def __init__(self):
        """
        Construct this filter/transformation.
        """
        super().__init__()

    def _initialize_params(self):
        super()._initialize_params()
        self._params.update(**dict(from_this_index=None,
                                   till_this_index=None,
                                   degree_threshold=5,
                                   window_width_seconds=10))

    def apply(self, data=None):
        """
        Leverage standard deviation to find where the data starts and ends.

        If the worker is not using the device and/or not working the standard
        deviation should be smaller than if working.
        """
        super().apply(data=data)

        params = self._params

        operate_on_columns = \
            DATA_FORMAT_CODES[params['data_format_code']]['NUMERICS']

        data_to_use = data.copy()
        data_to_use = data_to_use.loc[
                      params['from_this_index']:params['till_this_index'],
                      operate_on_columns]
        data_to_use = data_to_use.iloc[
                      params['from_this_index']:params['till_this_index']]

        if len(data_to_use) < 100:
            # due to the statistical nature of this filter, we need
            # data!
            raise Exception("We do not have enough data for this filter!")

        # window width in units of "indices" (# rows in data):
        width_indices = params['window_width_seconds'] * SAMPLING_RATE

        # (1) first apply to the beginning of the data:
        start_of_window = 0  # seconds
        end_of_window = start_of_window + width_indices
        window = data_to_use.iloc[start_of_window:end_of_window, :]
        move_by = width_indices // 2
        # how much is this initial data fluctuating in deg's?:
        window_std = window.std().max()

        window_moved = False
        while window_std < params['degree_threshold']:
            # still less than our threshold - so the real data has not
            # started yet:
            start_of_window += move_by
            end_of_window += move_by
            # move/slide window
            window = data_to_use.iloc[start_of_window:end_of_window, :]
            window_std = window.std().max()
            window_moved = True

        # take end point of window
        if window_moved:
            data_to_use = data_to_use.iloc[end_of_window:, :]

        # (2) next apply to the end of the data:
        if len(data_to_use) > width_indices:
            end_of_window = len(data_to_use) - 1
            start_of_window = end_of_window - width_indices

            window = data_to_use.iloc[start_of_window:end_of_window, :]
            # how much is this initial data fluctuating in deg's?:
            window_std = window.std().max()

            window_moved = False
            while window_std < params['degree_threshold']:
                # still less than our threshold - so the real data has not
                # started yet:
                start_of_window -= move_by  # move backwards (started at end)
                end_of_window -= move_by
                if start_of_window < 0:
                    break
                # move/slide window
                window = data_to_use.iloc[start_of_window:end_of_window, :]
                window_std = window.std().max()
                window_moved = True

            # take start point of window this time
            # (since we are walking backwards)
            if window_moved:
                data_to_use = data_to_use.iloc[:start_of_window, :]

        if len(data_to_use) == 0:
            raise Exception("This filter removed all data!")

        # now we have boxed in the data to a region of interest
        data_to_use = self._update_data(data_transformed=data)
        return data_to_use, {}
