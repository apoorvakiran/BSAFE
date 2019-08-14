# -*- coding: utf-8 -*-
"""

@ author Jesper Kristensen
"""

__all__ = ["LoadData"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import os
import requests
import numpy as np
import pandas as pd
from . import BaseData
from Settings import *


class LoadData(BaseData):

    def __init__(self):

        super().__init__()

        print("Data loading object created!")

    def _read_datafile(self, path=None, destination=None):
        """
        This methods helps read the datafile. There can be different formats of the data
        depending on the source and collection process. Here, we want to try to capture all of
        them.

        :return:
        """

        # suggested names
        # names = """Date-Time,Yaw[0](deg),Pitch[0](deg),Roll[0](deg),Yaw[1](deg),Pitch[1](deg),Roll[1](deg),DeltaYaw,DeltaPitch,DeltaRoll""".split(
        #     ',')
        names = COLUMN_NAMES_FORMAT_1
        try:
            # did the data come from google drive?
            local_path = self.download_from_google_drive(path=path, destination=destination)
            data = pd.read_csv(local_path, names=names)
            print('the data is from Google drive!')
        except:
            print("The data is local!")
            if not os.path.isfile(path):
                raise Exception(f"Could not find local file at '{path}'!")
            local_path = path

            # data is local - so try these names
            # names = """Date-Time,ax[0](mg),ay[0](mg),az[0](mg),gx[0](dps),gy[0](dps),gz[0](dps),mx[0](uT),my[0](uT),mz[0](uT),Yaw[0](deg),Pitch[0](deg),Roll[0](deg),ax[1](mg),ay[1](mg),az[1](mg),gx[1](dps),gy[1](dps),gz[1](dps),mx[1](uT),my[1](uT),mz[1](uT),Yaw[1](deg),Pitch[1](deg),Roll[1](deg)""".split(
            #     ',')
            names = COLUMN_NAMES_FORMAT_2

            # but... do we have to clean the data first?

            try:
                data = pd.read_csv(path, names=names)
                print("Successful loading of data with pandas read_csv...")

                # now, we want to make sure to skip certain rows until we have numerics.
                # We can use "az" as an example column:
                ix = 0
                while True:
                    try:
                        val = data.iloc[ix]['az[0](mg)']
                        if not is_numeric(val) or (np.isnan(float(val)) or data.iloc[ix].isna().any()):
                            # make sure we have values for all columns
                            ix += 1
                            continue
                        else:
                            break

                    except ValueError:
                        ix += 1
                data = data.iloc[ix:, :]

            except Exception as e:
                print("Found exception when straight loading the data from disk:")
                print(e)
                print("Now trying to load the data more carefully...")

                with open(path, 'r') as fd:
                    all_lines = fd.readlines()

                current_index = len(all_lines) - 1
                for ix, line in enumerate(all_lines):
                    line_split = line.split(',')
                    if len(line_split) == len(names) and (names[0] == line_split[0] and names[1] == line_split[1]):
                        start_index = ix  # the data starts here
                        if not start_index == current_index:
                            print("Success >> We found the start index of the data at {}!".format(start_index))

                end_index = None
                found_end = False
                while current_index > start_index:
                    # now walk backwards to find where the data ends
                    this_line = all_lines[current_index]

                    if len(this_line.split(',')) == len(names):
                        # found the end index
                        end_index = current_index
                        found_end = True
                        print("  > and we found the end index at {}".format(end_index))
                        break

                    current_index -= 1

                if not found_end:
                    print("Was unable to find the end point of the data?")
                    print("Printing the first 10 lines of data - maybe that can help debug this:")
                    print(all_lines[start_index:start_index:10])
                    raise Exception("Data format not currently handled")

                # now load the data:
                data = pd.read_csv(path, skiprows=start_index).iloc[:end_index - start_index]

        print(f"# of raw data points = {len(data)}")

        if len(data) <= 1:
            raise Exception("There is <= 1 data point(s) in the file '{}'".format(local_path))

        print("Checking that dates make sense...")

        # we need to find when the dates stop oscillating (sometimes b/w 2019 and 2000)...
        # we can use the standard deviation for this
        current_index = 0

        # demand that at least 70% of the data is useful

        print(f"Demanding that at least {FRACTION_OF_DATA_USEFUL * 100}% of "
              f"the data is useful!")
        last_index = int(data.shape[0] * FRACTION_OF_DATA_USEFUL)

        try:
            data['Date-Time'] = pd.to_datetime(data['Date-Time'])
        except ValueError as ve:
            # we need
            print("Got value error in trying to convert date-time:")
            print(ve)
            print("Please manually change this to the correct format!")
            raise

        print("loop to find if there are date-issues regarding back-and-forth in time, use std dev")

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

        if len(data) <= 1:
            raise Exception("There is <= 1 data point(s) in the file '{}'".format(local_path))

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

    def get_id(self, full_url=None):

        if full_url is None:
            raise Exception("The URL is None! Please provide a valid URL!")

        return full_url.split('id')[1][1:]

    def get_data(self, path=None, destination=None):

        if destination is None:
            print("Destination folder not provided, using current folder!")
            destination = '.'

        destination_dir = os.path.dirname(destination)
        if destination_dir and not os.path.isdir(destination_dir):
            os.makedirs(destination_dir)
            print("Creating destination directory {}".format(destination_dir))

        # So index "0" is the "wrist part" and "1" is the hand part.
        data = self._read_datafile(path=path)

        return data

    def download_from_google_drive(self, path=None, destination=None):

        file_id = self.get_id(path)
        URL = "https://docs.google.com/uc?export=download"
        session = requests.Session()

        response = session.get(URL, params={'id' : file_id}, stream=True)
        token = self.get_confirm_token(response)

        if token:
            params = { 'id' : id, 'confirm' : token }
            response = session.get(URL, params = params, stream = True)

        self.save_response_content(response, destination)

        return destination

    def get_confirm_token(self, response=None):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(self, response=None, destination=None):

        CHUNK_SIZE = 32768

        print("Storing file to disk...")
        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
        print("Done storing to disk!")


def is_numeric(val):
    try:
        float(val)
        return True
    except Exception:
        return False
