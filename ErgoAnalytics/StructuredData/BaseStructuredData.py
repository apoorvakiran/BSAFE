# -*- coding: utf-8 -*-
"""
This is the Base code of the structured data.

@ author Jesper Kristensen, Jacob Tyrrell
Copyright 2018
"""

__all__ = ["BaseStructuredData"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import logging
import numpy as np
import pandas as pd
from .. import is_numeric
from Settings import FRACTION_OF_DATA_USEFUL

logger = logging.getLogger()

class BaseStructuredData(object):
    """
    Base class of a structured data object.
    """

    _name = None

    def __init__(self, name=None):
        """
        """

        self._name = name

    @property
    def name(self):
        return self._name

    def _pre_process_data(self, data=None, names=None, is_streaming=False):
        """
        Take an incoming DataFrame in an alleged correct format and check
        the data quality and format. The output is a DataFrame containing
        valuable data.

        :param data:
        :param names:
        :param is_streaming: Helps with some data checks where there is just
        1 element (which is fine for streaming, but not great if loading a
        supposedly "entire, say, 8-hour work task")

        :return:
        """

        logger.info(f"# of raw data points = {len(data)}")

        if len(data) <= 1:
            raise Exception("There is <= 1 data point(s) in the file!")

        logger.info("Checking that dates make sense...")

        # demand that at least 70% of the data is useful
        logger.info(f"Demanding that at least {FRACTION_OF_DATA_USEFUL * 100}% of "
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
            logger.info("Got value error in trying to convert date-time:")
            logger.info(ve)
            logger.info("Please manually change this to the correct format!")
            raise

        logger.info("loop to find if there are date-issues regarding back-and-forth "
              "in time, use std dev")

        data = BaseStructuredData._sigma_filter(data, last_index=last_index)

        # check that we have data left after filter:
        if not is_streaming and len(data) <= 1:
            raise Exception("There is <= 1 data point(s) in the file!")

        self._delta_t_filter(data, is_streaming=is_streaming)
        self._data_imputation_filter(data)

        try:
            # shape of data before filtering the specific names
            # we are asking for:
            logger.info("  > Before getting the relevant columns the data has # of "
                  "columns = {} (len names = {})".format(data.shape[1],
                                                         len(names)))
            data = data[names]  # just get the names above
            logger.info("  > After getting the relevant columns the data has # of "
                  "columns = {}".format(data.shape[1]))
        except KeyError:
            logger.info("Looks like the delta values may not be in the data? "
                  "Delta yaw etc.? So skipping the last 3 columns")
            # delta values may not be in the index, so ignore those:
            data = data[names[:-3]]

        # now we have the filtered data;
        # make sure to sort it by date:
        logger.info("Sorting the data by time...")

        data.sort_values(by=['Date-Time'], ascending=True, inplace=True)

        logger.info("Dropping duplicates...")
        logger.info("    # rows before = {}".format(len(data)))
        data.drop_duplicates(subset=['Date-Time'], inplace=True)
        logger.info("    # rows after = {}".format(len(data)))
        # we should reset the index too
        logger.info("Resetting the index too")
        data = data.reset_index(drop=True)
        logger.info(f"Summary: # of data points after basic pre-processing: "
              f"{len(data)}")

        if not is_streaming and len(data) <= 1:
            logger.info("The data was in a bad quality - we only have 1 data point "
                  "left after some basic pre-processing!")
            raise Exception("Bad quality data")

        return data

    @staticmethod
    def _sigma_filter(data=None, last_index=None):
        """
        Apply sigma filter (standard deviation filter) to find out when
        the device started collecting stable time points.

        Basically: We need to find when the dates stop oscillating
        (sometimes b/w 2019 and 2000)...
        we can use the standard deviation (hence sigma) for this.

        :param data:
        :param last_index:
        :return:
        """
        # compute standard deviation vs index:

        assert last_index and last_index > 0

        current_index = 0
        all_std_sec = []
        while current_index < last_index:

            # current std dev:
            try:
                this_std_sec = \
                    data['Date-Time'].iloc[current_index:
                                           last_index].diff().std().seconds
            except Exception:
                raise Exception("Could not compute standard deviation?")
            all_std_sec.append(this_std_sec)
            status = np.abs(np.diff(all_std_sec))

            if len(status) > 0 and status[-1] < 1e-10:
                break

            current_index += 1  # move it

        return data.iloc[max(0, current_index - 1):, :]

    def _delta_t_filter(self, data=None, is_streaming=False):
        """
        Check that the delta time between measurements is reasonable.
        Currently just a very simple sanity check but can be expanded.

        If the data is "streaming" we may just get a single datum in which
        case we don't check.

        :param data:
        :param is_streaming:
        :return:
        """

        if (not is_streaming) and \
                (not (pd.to_datetime(data['Date-Time']).iloc[1] -
                      pd.to_datetime(data['Date-Time']).iloc[0]).seconds <= 1):
            logger.info("The data seems to have a difference in time of 1 "
                  "second or more?")
            logger.info("The frequency is expected to be closer to 1/100th of a "
                  "second!")
            logger.info("Please double-check the date-times.")
            raise Exception("Date-time frequency error in collection!")

    def _data_imputation_filter(self, data=None, method='nan_filter'):
        """
        Imputes the data or rids of it depending on the method used.

        :param data:
        :return:
        """

        # right now the data imputation is easy: Just get rid
        # of the NaN values - but going forward we can have more
        # complex methods such as sampling from statistical distributions:
        # For example: Create a multi-variate Gaussian on all data we do have
        # and then sample from it conditioned on the data we _do_ have at other
        # rows to find likely values for the missing data.
        if method == 'nan_filter':
            logger.info("> # of data before filtering for NaNs... = "
                  "{}".format(len(data)))
            data.dropna(how='any', inplace=True)
            logger.info("> # of data after filtering away NaNs... = "
                  "{}".format(len(data)))
        else:
            raise NotImplementedError("Implement me!")
