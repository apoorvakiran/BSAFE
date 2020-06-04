# -*- coding: utf-8 -*-
"""
Loads data from a flat file from disk. The most basic data loader.
Just provide data which has, say, been downloaded from the hardware to disk.

The code is simple since no checks are done - this is postponed to the
structured data loader.

@ author Jesper Kristensen
Copyright Iterate Labs, Inc.
"""

__all__ = ["LoadDataFromLocalDisk"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import os
import numpy as np
import pandas as pd
from . import BaseData
from .. import is_numeric
from constants import *
import logging

logger = logging.getLogger()


class LoadDataFromLocalDisk(BaseData):
    """
    Loads data from disk on local harddrive. Simplest form of loading data.
    """

    def __init__(self):

        super().__init__()

        logger.debug("Data loading object created!")

    def _read_datafile(self, path=None, data_format_code="3"):
        """
        This methods helps read a datafile. There can be different
        formats of the data depending on the source and collection process
        which is what "data_format_code" is capturing. See "Settings" folder
        in the main repo for more on this.

        :return: Pandas DataFrame with data loaded from disk.
        """

        data_column_names = DATA_FORMAT_CODES[data_format_code]["NAMES"]
        self._data_column_names = data_column_names

        if not os.path.isfile(path):
            msg = f"Could not find local file at '{path}'!"
            logger.error(msg)
            raise Exception(msg)

        try:
            data = pd.read_csv(path, names=self.data_column_names)

            logger.debug("Successful loading of data...")

            data = self._find_numeric_and_correct_columns(data, data_format_code=data_format_code)

        except Exception as e:
            logger.warning(
                "There was an error loading the data from disk " "directly, taking extra precaution, the error was:"
            )
            logger.warning(e)
            logger.warning(">> Now trying to load the data more carefully...")

            with open(path, "r") as fd:
                all_lines = fd.readlines()

            start_index = None
            current_index = len(all_lines) - 1
            for ix, line in enumerate(all_lines):
                line_split = line.split(",")
                if len(line_split) == len(self.data_column_names) and (
                    self.data_column_names[0] == line_split[0] and self.data_column_names[1] == line_split[1]
                ):
                    start_index = ix  # the data starts here
                    if not start_index == current_index:
                        logger.debug("Success >> We found the start index of " "the data at {}!".format(start_index))

            if not start_index:
                # we cannot recover
                msg = "Was unable to find start index in the data!"
                logger.error(msg)
                raise Exception(msg)

            end_index = None
            found_end = False
            while current_index > start_index:
                # now walk backwards to find where the data ends
                this_line = all_lines[current_index]

                if len(this_line.split(",")) == len(self.data_column_names):
                    # found the end index
                    end_index = current_index
                    found_end = True
                    logger.debug("  > and we found the end " "index at {}".format(end_index))
                    break

                current_index -= 1

            if not found_end:
                logger.debug("Was unable to find the end point of the data?")
                logger.debug("Printing the first 10 lines of data - maybe that " "can help debug this:")
                logger.debug(all_lines[start_index:start_index:10])
                msg = "Data format not currently handled"
                logger.error(msg)
                raise Exception(msg)

            # now actually load the part of the file that has good data:
            data = pd.read_csv(path, skiprows=start_index).iloc[: end_index - start_index]

        data = self._cast_to_correct_types(all_data=data, data_format_code=data_format_code)

        return data

    def get_data(self, path=None, destination=None, data_format_code="3"):
        """
        Returns the data given a path and destination folder. The data
        format code is provided as well to tell BSAFE which data format
        is being loaded (each different format is another way to load data
        from the device).

        :param path:
        :param destination:
        :param data_format_code: Which format is the data in? Refer to the
        settings module.
        :return:
        """

        if destination is None:
            logger.info("Destination folder not provided, using " "current folder!")
            destination = "."

        destination_dir = os.path.abspath(destination)
        if destination_dir and not os.path.isdir(destination_dir):
            os.makedirs(destination_dir)
            logger.info("Creating destination " "directory {}".format(destination_dir))

        if not os.path.isdir(destination_dir):
            msg = "Not a valid destination " 'directory "{}"!'.format(destination_dir)
            logger.error(msg)
            raise Exception(msg)

        data = self._read_datafile(path=path, data_format_code=data_format_code)

        data = data.reset_index(drop=True, inplace=False)

        return data

    @staticmethod
    def _find_numeric_and_correct_columns(data=None, data_format_code="3"):
        """
        The following code ensures that we skip rows until we reach
        numeric values and we have all the columns we seek.
        """

        # pick any of the numeric columns
        numeric_variable_name = DATA_FORMAT_CODES[data_format_code]["NUMERICS"][0]

        # now, we want to make sure to skip certain rows until we
        # have numerics.
        # We can use "az" as an example column:
        ix = 0
        while True:
            try:
                val = data.iloc[ix][numeric_variable_name]
                if not is_numeric(val) or (np.isnan(float(val)) or data.iloc[ix].isna().any()):
                    # make sure we have values for all columns
                    ix += 1
                    continue
                else:
                    break

            except ValueError:
                ix += 1

        return data.iloc[ix:, :]
