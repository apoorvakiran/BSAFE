# -*- coding: utf-8 -*-
"""
Here we share some basic data interface across all our data parser classes.
For example, we have a "static" data loader and a "streaming" data loader.
These both share some commonalities captured here.

@ author Jesper Kristensen
Copyright 2018
"""

__all__ = ["BaseData"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"


class BaseData(object):

    _data_column_names = None  # name of columns in the data

    def __init__(self):
        pass

    @property
    def data_column_names(self):
        return self._data_column_names
