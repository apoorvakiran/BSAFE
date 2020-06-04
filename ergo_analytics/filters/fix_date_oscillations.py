# -*- coding: utf-8 -*-
"""

@ author Jesper Kristensen
Copyright 2018-
"""

__all__ = ["FixDateOscillations"]
__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

from pandas import DataFrame
from pandas import to_datetime
from . import BaseTransformation
from constants import DATA_FORMAT_CODES
from constants import DATE


class FixDateOscillations(BaseTransformation):
    """
    Finds when the time starts producing incrementing meaningful values.

    What could happen with the hardware is that time points are collected
    which oscillate between year 2000 and current time.

    So if we were to plot all the time points we should find that one
    group of points are <2015, say, and another are later. We can then
    just filter out the earlier ones.
    """

    def __init__(self):
        super().__init__()

    def _initialize_params(self):
        super()._initialize_params()
        self._params.update(**dict(cut_off_date="2015-01-01"))

    def apply(self, data=None, **kwargs):
        """
        Finds when the time starts producing incrementing meaningful values.

        :param data:
        :param last_index:
        :return:
        """
        super().apply(data=data, **kwargs)

        date_column = "Date-Time"

        # this filter does require the date to be present
        dates_as_int = data[date_column].apply(lambda x: x.asm8.astype(int))

        # data before this is considered wrong:
        cut_off_date = self._params["cut_off_date"]
        cut_off_date_as_int = to_datetime(cut_off_date).asm8.astype(int)

        if (dates_as_int > cut_off_date_as_int).all():
            # no oscillations occurring, just return
            return data, {}

        # since we didn't return we know that some dates are off
        first_normal_data_point = dates_as_int[dates_as_int < cut_off_date_as_int].index.max() + 1

        data = data.iloc[first_normal_data_point:, :]

        data_to_use = self._update_data(data_transformed=data, columns_operated_on=date_column)
        return data_to_use, {"updated": date_column}
