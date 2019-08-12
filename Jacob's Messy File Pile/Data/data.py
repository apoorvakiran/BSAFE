# -*- coding: utf-8 -*-
"""
@ author Jesper Kristensen
"""

__all__ = ["LoadData"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import os
import requests
import pandas as pd


class LoadData:

    def __init__(self):

        print("Data loading object created!")

    def _read_datafile(self, path=None, destination=None):
        """
        This methods helps read the datafile. There can be different formats of the data
        depending on the source and collection process. Here, we want to try to capture all of
        them.
        :return:
        """

        # suggested names
        names = """Date-Time,Yaw[0](deg),Pitch[0](deg),Roll[0](deg),Yaw[1](deg),Pitch[1](deg),Roll[1](deg),DeltaYaw,DeltaPitch,DeltaRoll""".split(
            ',')
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
            names = """Date-Time,ax[0](mg),ay[0](mg),az[0](mg),gx[0](dps),gy[0](dps),gz[0](dps),mx[0](uT),my[0](uT),mz[0](uT),Yaw[0](deg),Pitch[0](deg),Roll[0](deg),ax[1](mg),ay[1](mg),az[1](mg),gx[1](dps),gy[1](dps),gz[1](dps),mx[1](uT),my[1](uT),mz[1](uT),Yaw[1](deg),Pitch[1](deg),Roll[1](deg)""".split(
                ',')
            # but... do we have to clean the data first?
            try:
                data = pd.read_csv(path, names=names)
                print("Successful loading of data with pandas read_csv...")
            except Exception as e:
                print("Found exception when straight loading the data from disk.")
                print("Trying to load the data more carefully...")

                with open(path, 'r') as fd:
                    all_lines = fd.readlines()

                current_index = len(all_lines) - 1
                for ix, line in enumerate(all_lines):
                    line_split = line.split(',')
                    if len(line_split) == len(names) and (names[0] == line_split[0] and names[1] == line_split[1]):
                        start_index = ix  # the data starts here
                        if not start_index == current_index:
                            print("Succes >> We found the start index of the data at {}!".format(start_index))

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
        last_index = int(data.shape[0] * 0.7)

        data['Date-Time'] = pd.to_datetime(data['Date-Time'])

        print("loop!")

        import numpy as np

        # compute standard deviation vs index:
        all_std_sec = []
        while current_index < last_index:

            # current std dev:
            this_std_sec = data['Date-Time'].iloc[current_index:last_index].diff().std().seconds
            all_std_sec.append(this_std_sec)

            status = np.abs(np.diff(all_std_sec))

            if len(status) > 0 and status[-1] < 1e-10:
                break

            current_index += 1  # move it

        data = data.iloc[max(0, current_index - 1):, :]

        if len(data) <= 1:
            raise Exception("There is <= 1 data point(s) in the file '{}'".format(local_path))

        # sanity check:
        assert (pd.to_datetime(data['Date-Time']).iloc[1] - pd.to_datetime(data['Date-Time']).iloc[0]).seconds < 1

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
        data.drop_duplicates(subset=['Date-Time'], inplace=True)
        # we should reset the index too
        print("Resetting the index too")
        data = data.reset_index(drop=True)
        print(f"# of data points after basic pre-processing: {len(data)}")

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