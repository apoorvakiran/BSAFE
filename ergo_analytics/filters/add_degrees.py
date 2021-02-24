# -*- coding: utf-8 -*-
"""This transformed adds a custom angular degree amount to the data.

@ author Jesper Kristensen
Copyright 2018-
All Rights Reserved.
"""

__all__ = ["AddDegrees"]
__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

from . import BaseTransformation
from constants import DATA_FORMAT_CODES


class AddDegrees(BaseTransformation):
    """This filter can add an arbitrary amount of degrees to the data."""

    def __init__(self):
        super().__init__()

    def _initialize_params(self):
        super()._initialize_params()

    def apply(self, data=None, **kwargs):
        """Applies this filter to the incoming data.

        :param data:
        :return:
        """
        super().apply(data=data, **kwargs)

        params = self._params
        if "degrees" in params:
            dict_add_this = params["degrees"]  # {"Yaw[0]": 40, ...}
        else:
            return data, {}

        data_transformed = data.copy()
        operate_on_columns = []
        for col in dict_add_this:
            if col in data:
                data_transformed.loc[:, col] += dict_add_this[col]
                operate_on_columns.append(col)

        return (
            self._update_data(
                data_transformed=data_transformed,
                columns_operated_on=operate_on_columns,
            ),
            {"updated": operate_on_columns},
        )
