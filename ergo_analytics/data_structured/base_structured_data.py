# -*- coding: utf-8 -*-
"""This is the Base code of the structured data.

@ author Jesper Kristensen
Copyright 2018- Iterate Labs, Inc.
All Rights Reserved.
"""

__all__ = ["BaseStructuredData"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import logging

logger = logging.getLogger()


class BaseStructuredData(object):
    """
    Base class of a structured data object.
    """

    _name = None

    def __init__(self, name=None):
        """
        Construct the base class.
        """
        self._name = name

    @property
    def name(self):
        return self._name
