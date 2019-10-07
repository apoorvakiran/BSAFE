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

    def __init__(self, columns=None):
        if columns is None:
            raise Exception("Please provide a valid set of columns")
        self._columns = columns

    def apply(self, data=None):
        raise NotImplementedError("Implement me!")
