# -*- coding: utf-8 -*-
"""Preprocess the incoming data.

@ author Jesper Kristensen
Copyright Iterate Labs Inc.
All Rights Reserved.
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

__all__ = ["Preprocess"]

import datetime
import pandas as pd

from constants import DATA_FORMAT_CODES
from ergo_analytics.filters import BaseTransformation


class Preprocess(BaseTransformation):
    """Pre-process the data."""

    def __init__(self):
        super().__init__()

    def _initialize_params(self):
        super()._initialize_params()
        self._params.update(**dict(index_range=None))

    def apply(self, data=None, **kwargs):
        """
        Applies a quadrant filter to the incoming data.

        :param data:
        :param units: what are the units of the data? Degrees?
        :return:
        """
        super().apply(data=data, **kwargs)

        # nothing special right now...
        params = self._params
        only_process_index_range = params.get('index_range', None)
        force_new_timestamps = params.get('force_new_timestamps', False)

        rows_were_cut = False
        if only_process_index_range is not None:
            data_transformed = data.iloc[only_process_index_range[0]:only_process_index_range[1]]
            rows_were_cut = True
        else:
            # do nothing
            data_transformed = data

        columns_to_use = list(data.columns)

        date_column = DATA_FORMAT_CODES[params['data_format_code']]['TIMESTAMP']

        if force_new_timestamps:
            # ensure that we have unique timestamps
            # (can prevent any time-stamp formatting issues)

            # just make up some timestamps but ensure a frequency of
            # 1/10th of a second between each:
            # start from today:
            freq = 1 / 10
            start_date = datetime.datetime.utcnow()

            new_dates = [start_date - datetime.timedelta(seconds=freq * ix)
                         for ix in range(len(data_transformed))]

            new_dates = new_dates[::-1]
            data_transformed.loc[:, 'Date-Time'] = new_dates

        data_transformed[date_column] = pd.to_datetime(data_transformed[date_column])

        actions_taken = {'action': [f'rows were cut to the range: '
                          f'({data_transformed.index[0]}, '
                          f'{data_transformed.index[-1]})' if rows_were_cut else 'nothing']}
        if force_new_timestamps:
            actions_taken['action'].append("new timestamps replaced old ones.")

        return self._update_data(data_transformed=data_transformed,
                                 row_operation=True,
                                 columns_operated_on=columns_to_use), \
               actions_taken
