# -*- coding: utf-8 -*-
"""
Loads data from a flat file from disk. The most basic data loader.
Just provide data which has, say, been downloaded from the hardware to disk.

The code is simple since no checks are done - this is postponed to the
structured data loader.

@ author Jesper Kristensen
"""

__all__ = ["LoadDataFromLocalDisk"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import os
import numpy as np
import pandas as pd
from . import BaseData
from .. import is_numeric
from Settings import *


class LoadDataFromLocalDisk(BaseData):
    """
    Loads data from disk on local harddrive. Simplest form of loading data.
    """

    def __init__(self):

        super().__init__()

        print("Data loading object created!")

    def _read_datafile(self, path=None, data_format_code='3'):
        """
        This methods helps read the datafile. There can be different
        formats of the data depending on the source and collection process.
        Here, we want to try to capture all of them.

        :return: Pandas DataFrame with data loaded from disk.
        """

        data_column_names = DATA_FORMAT_CODES[data_format_code]
        self._data_column_names = data_column_names

        if not os.path.isfile(path):
            raise Exception(f"Could not find local file at '{path}'!")

        try:
            data = pd.read_csv(path, names=self.data_column_names)
            print("Successful loading of data...")

            data = self._find_numeric_and_correct_columns(data)

        except Exception as e:
            print("Found exception when straight loading the "
                  "data from disk:")
            print(e)
            print("Now trying to load the data more carefully...")

            with open(path, 'r') as fd:
                all_lines = fd.readlines()

            start_index = None
            current_index = len(all_lines) - 1
            for ix, line in enumerate(all_lines):
                line_split = line.split(',')
                if len(line_split) == len(self.data_column_names) and \
                        (self.data_column_names[0] == line_split[0] and
                         self.data_column_names[1] == line_split[1]):
                    start_index = ix  # the data starts here
                    if not start_index == current_index:
                        print("Success >> We found the start index of "
                              "the data at {}!".format(start_index))

            if not start_index:
                raise Exception("Was unable to find start index in the data!")

            end_index = None
            found_end = False
            while current_index > start_index:
                # now walk backwards to find where the data ends
                this_line = all_lines[current_index]

                if len(this_line.split(',')) == len(self.data_column_names):
                    # found the end index
                    end_index = current_index
                    found_end = True
                    print("  > and we found the end "
                          "index at {}".format(end_index))
                    break

                current_index -= 1

            if not found_end:
                print("Was unable to find the end point of the data?")
                print("Printing the first 10 lines of data - maybe that "
                      "can help debug this:")
                print(all_lines[start_index:start_index:10])
                raise Exception("Data format not currently handled")

            # now load the data:
            data = pd.read_csv(path,
                               skiprows=start_index).iloc[:end_index -
                                                           start_index]

        return data

    def get_data(self, path=None, destination=None, data_format_code='3'):
        """

        :param path:
        :param destination:
        :param data_format_code: Which format is the data in? Refer to the
        settings module.
        :return:
        """

        if destination is None:
            print("Destination folder not provided, using current folder!")
            destination = '.'

        destination_dir = os.path.dirname(destination)
        if destination_dir and not os.path.isdir(destination_dir):
            os.makedirs(destination_dir)
            print("Creating destination directory {}".format(destination_dir))

        data = self._read_datafile(path=path, data_format_code=data_format_code)

        return data

    def _find_numeric_and_correct_columns(self, data=None,
                                          data_format_code='3'):
        """the following code ensures that we skip rows until we reach
        numeric values and we have all the columns we seek
        """

        if data_format_code == '3':
            numeric_variable_name = 'az[0](mg)'
        elif data_format_code == '4':
            numeric_variable_name = 'DeltaYaw'
        else:
            numeric_variable_name = 'az[0]'

        # now, we want to make sure to skip certain rows until we
        # have numerics.
        # We can use "az" as an example column:
        ix = 0
        while True:
            try:
                val = data.iloc[ix][numeric_variable_name]
                if not is_numeric(val) or (np.isnan(float(val)) or
                                           data.iloc[ix].isna().any()):
                    # make sure we have values for all columns
                    ix += 1
                    continue
                else:
                    break

            except ValueError:
                ix += 1

        return data.iloc[ix:, :]
