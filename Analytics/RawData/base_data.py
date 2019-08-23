# -*- coding: utf-8 -*-
"""
Here we share some basic data interface.

@ author Jesper Kristensen
Copyright 2018
"""

__all__ = ["BaseData"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import numpy as np
import pandas as pd
from Settings import *


class BaseData(object):

    def __init__(self):
        pass

    def _check_data(self, data=None, names=None, file_path=None):
        """
        Take an incoming DataFrame in an alleged correct format and check
        the data quality and format. The output is a DataFrame containing
        valuable data.

        :param data:
        :param names:
        :param file_path:
        :return:
        """

        print(f"# of raw data points = {len(data)}")

        if file_path and len(data) <= 1:
            raise Exception("There is <= 1 data point(s) in the "
                            "file '{}'".format(file_path))

        print("Checking that dates make sense...")

        # we need to find when the dates stop oscillating
        # (sometimes b/w 2019 and 2000)...
        # we can use the standard deviation for this
        current_index = 0

        # demand that at least 70% of the data is useful

        print(f"Demanding that at least {FRACTION_OF_DATA_USEFUL * 100}% of "
              f"the data is useful!")
        last_index = int(data.shape[0] * FRACTION_OF_DATA_USEFUL)

        try:
            try:
                data['Date-Time'] = pd.to_datetime(data['Date-Time'])
            except IndexError:
                raise Exception("It looks like the incoming data does not "
                                "have the 'Date-Time' column in it?! - please "
                                "check the data format")
        except ValueError as ve:
            # we need
            print("Got value error in trying to convert date-time:")
            print(ve)
            print("Please manually change this to the correct format!")
            raise

        print("loop to find if there are date-issues regarding back-and-forth "
              "in time, use std dev")

        # compute standard deviation vs index:
        all_std_sec = []
        while current_index < last_index:

            # current std dev:
            try:
                this_std_sec = data['Date-Time'].iloc[current_index:last_index].diff().std().seconds
            except:

                import pdb
                pdb.set_trace()
            all_std_sec.append(this_std_sec)
            status = np.abs(np.diff(all_std_sec))

            if len(status) > 0 and status[-1] < 1e-10:
                break

            current_index += 1  # move it

        data = data.iloc[max(0, current_index - 1):, :]

        if file_path and len(data) <= 1:
            raise Exception("There is <= 1 data point(s) in the file '{}'".format(file_path))

        # sanity check:
        if not (pd.to_datetime(data['Date-Time']).iloc[1] - pd.to_datetime(data['Date-Time']).iloc[0]).seconds <= 1:
            print("The data seems to have a difference in time of 1 second or more?")
            print("The frequency is expected to be closer to 1/100th of a second!")
            print("Please double-check the date-times.")
            raise Exception("Date-time frequency error in collection!")

        # import numpy as np
        # import matplotlib.pyplot as plt
        # plt.subplot(211)
        # plt.plot(data['Date-Time'].iloc[:600])
        # plt.subplot(212)
        # plt.plot(np.abs(np.diff(all_std_sec)))
        # plt.axhline(1)
        # plt.ylim(0, 100)
        # plt.show()

        print("> # of data before filtering for NaNs... = {}".format(len(data)))
        data.dropna(how='any', inplace=True)
        print("> # of data after filtering away NaNs... = {}".format(len(data)))

        try:
            # shape of data before filtering the specific names we are asking for:
            print("  > Before getting the relevant columns the data has # of columns = {} (len names = {})".format(data.shape[1], len(names)))
            data = data[names]  # just get the names above
            print("  > After getting the relevant columns the data has # of columns = {}".format(data.shape[1]))
        except KeyError:
            print("Looks like the delta values may not be in the data? Delta yaw etc.? So skipping the last 3 columns")
            # delta values may not be in the index, so ignore those:
            data = data[names[:-3]]

        # now we have the raw data, make sure to sort it by date
        print("Sorting the data by time...")

        data.sort_values(by=['Date-Time'], ascending=True, inplace=True)
        print("Dropping duplicates...")
        print("    # rows before = {}".format(len(data)))
        data.drop_duplicates(subset=['Date-Time'], inplace=True)
        print("    # rows after = {}".format(len(data)))
        # we should reset the index too
        print("Resetting the index too")
        data = data.reset_index(drop=True)
        print(f"Summary: # of data points after basic pre-processing: {len(data)}")

        if len(data) <= 1:
            print("The data was in a bad quality - we only have 1 data point left after some basic pre-processing!")
            raise Exception("Bad quality data")

        return data
