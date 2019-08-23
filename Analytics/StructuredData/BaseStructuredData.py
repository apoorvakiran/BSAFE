# -*- coding: utf-8 -*-
"""
Holds an Experiment object and everything related to it.

@ author Jesper Kristensen, Jacob Tyrrell
Copyright 2018
"""

__all__ = ["BaseStructuredData"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"


class BaseStructuredData(object):
    """
    Base class of a structured data object.
    """

    _name = None

    def __init__(self, name=None):
        """
        """

        self._name = name

        # TODO: transfer common methods b/w static and streaming here...


    @property
    def name(self):
        return self._name
