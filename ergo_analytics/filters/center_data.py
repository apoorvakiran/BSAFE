# -*- coding: utf-8 -*-
"""
This transformation centers data, i.e., it subtracts out the mean.

@ author Jesper Kristensen
Copyright 2018-
"""

__all__ = ["DataCentering"]
__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

from . import BaseTransformation
from constants import DATA_FORMAT_CODES


class DataCentering(BaseTransformation):
    """
    Responsible for centering incoming data.
    """

    def __init__(self):
        super().__init__()

    def _initialize_params(self):
        super()._initialize_params()  # no additional parameters for this filter

    def apply(self, data=None, **kwargs):
        """
        Applies this filter to the incoming data.

        :param data:
        :return:
        """
        super().apply(data=data, **kwargs)

        params = self._params
        if "center_these_columns" in params:
            operate_on_columns = params["center_these_columns"]
        else:
            if "data_format_code" in params and params["data_format_code"] is not None:
                operate_on_columns = DATA_FORMAT_CODES[params["data_format_code"]][
                    "NUMERICS"
                ]
            else:
                operate_on_columns = list(data.columns)

        data_centered = data.loc[:, operate_on_columns]
        data_centered -= data_centered.mean(axis=0)

        return (
            self._update_data(
                data_transformed=data_centered, columns_operated_on=operate_on_columns
            ),
            {"updated": operate_on_columns},
        )
