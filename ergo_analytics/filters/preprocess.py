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

        rows_were_cut = False
        if only_process_index_range is not None:
            data_transformed = data.iloc[only_process_index_range[0]:only_process_index_range[1]]
            rows_were_cut = True
        else:
            # do nothing
            data_transformed = data

        columns_to_use = list(data.columns)

        date_column = DATA_FORMAT_CODES[params['data_format_code']]['TIMESTAMP']

        data_transformed[date_column] = pd.to_datetime(data_transformed[date_column])

        return self._update_data(data_transformed=data_transformed,
                                 row_operation=True,
                                 columns_operated_on=columns_to_use),\
               {'action': f'rows were cut to the range: '
                          f'({data_transformed.index[0]}, '
                          f'{data_transformed.index[-1]}' if rows_were_cut else 'nothing'}
