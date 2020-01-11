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

from . import BaseTransformation


class Preprocess(BaseTransformation):
    """
    Applies the quadrant filter to structured data arising at
    times due primarily to Gimball lock.
    """

    def __init__(self):
        super().__init__()

    def _initialize_params(self):
        super()._initialize_params()
        self._params.update(**dict(units='deg'))

    def apply(self, data=None, **kwargs):
        """
        Applies a quadrant filter to the incoming data.

        :param data:
        :param units: what are the units of the data? Degrees?
        :return:
        """
        super().apply(data=data, **kwargs)

        # nothing special right now...

        return self._update_data(data_transformed=data_transformed,
                                 columns_operated_on=columns_to_use), {}
