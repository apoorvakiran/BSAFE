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

from constants import DATA_FORMAT_CODES
import logging
logger = logging.getLogger()


class BaseData(object):

    _data_column_names = None  # name of columns in the data
    _number_of_points = None

    def __init__(self):
        pass

    @property
    def data_column_names(self):
        return self._data_column_names

    @property
    def number_of_points(self):
        return self._number_of_points

    def _cast_to_correct_types(self, all_data=None, data_format_code='4'):
        """
        Makes sure the data is in the format expected from its streaming type.

        :param all_data: pd.DataFrame containing data.
        :param data_format_code: what is the streaming type of data?
        :return:
        """
        if all_data is None:
            msg = "Please provide valid data!"
            logger.exception(msg)
            raise Exception(msg)

        # now convert data based on the types we know:
        data_column_names = DATA_FORMAT_CODES[data_format_code]['NAMES']
        data_column_types = DATA_FORMAT_CODES[data_format_code]['TYPES']
        all_data = all_data.apply(dict(zip(data_column_names, data_column_types)))

        # make sure index is ints (can convert to "float64" if there are
        # some NaNs here and there):
        all_data.index = list(map(int, all_data.index))

        self._number_of_points = len(all_data)

        return all_data
