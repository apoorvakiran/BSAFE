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
    _columns_operated_on = None
    _initial_data = None
    _params = None

    def __init__(self, params=None):

        # set default params:
        self._initialize_params()

        # potentially override with incoming parameters on initiation:
        if params is not None:
            self._params.update(**params)

    @property
    def columns_operated_on(self):
        return self._columns_operated_on

    def _initialize_params(self):
        """Each filter implements its own set of
        default parameters."""
        self._params = dict(data_format_code="5")

    def apply(self, data=None, parameters=None):
        self._initial_data = data

        if parameters:
            # have ability to pass in parameters via a cache:
            for param in parameters:
                if param in self._params:
                    self._params[param] = parameters[param]

    def update(self, new_params=None):
        """
        Updates the filter.
        """
        if new_params is None:
            # raise Exception("Incoming parameters are None!")
            return

        self._params.update(**new_params)

    def _update_data(self, data_transformed=None, row_operation=False, columns_operated_on=None):
        """
        Makes sure to update the incoming data to the transformed data
        but leave incoming columns in place and potentially add new columns.
        """

        if row_operation:
            # we operated on the rows, not the columns
            return data_transformed

        data_to_return = self._initial_data
        for col in data_transformed:
            data_to_return[col] = data_transformed[col]

        self._columns_operated_on = columns_operated_on
        return data_to_return

    def get_parameters(self):
        """
        Returns the parameters of this filter.
        """
        return self._params
