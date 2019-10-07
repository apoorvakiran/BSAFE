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


class DataCentering(BaseTransformation):
    """
    Responsible for centering incoming data.
    """

    def __init__(self, columns=None):
        super().__init__(columns=columns)

    def apply(self, data=None):
        """
        Applies this filter to the incoming data.

        :param data:
        :return:
        """

        if self._columns == 'all':
            self._columns = data.columns

        data_centered = data[self._columns]
        data_centered -= data_centered.mean(axis=0)

        return data_centered
