# -*- coding: utf-8 -*-
"""
Defines filters that can be applied to data.

@ author Iterate Labs, Inc.
Copyright 2018-
"""

import logging

__all__ = ["BaseTransformation"]
__author__ = "Iterate Labs, Inc."
__version__ = "Alpha"

logger = logging.getLogger()


class BaseTransformation(object):
    """
    Applies a transformation to the data.
    """

    _columns = None
    _initial_data = None
    _params = None

    def __init__(self, columns=None, params=None):

        if columns is None:
            raise Exception("Please provide a valid set of columns")
        if columns and not isinstance(columns, str):
            self._columns = list(columns)

        # set default params:
        self._initialize_params()

        # potentially override with incoming parameters on initiation:
        if params is not None:
            self._params.update(**params)

    def _initialize_params(self):
        """
        Each filter implements its own set of default parameters.
        """
        raise NotImplementedError("Implement me!")

    def apply(self, data=None):
        self._initial_data = data

    def update(self, new_params=None):
        """
        Updates the filter.
        """
        if new_params is None:
            # raise Exception("Incoming parameters are None!")
            return

        self._params.update(**new_params)

    def _update_data(self, data_transformed=None):
        """
        Makes sure to update the transformed data.
        """
        data_to_return = self._initial_data
        for col in data_transformed:
            data_to_return[col] = data_transformed[col]
        return data_to_return
