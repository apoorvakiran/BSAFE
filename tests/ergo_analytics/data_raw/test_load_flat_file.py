# -*- coding: utf-8 -*-
"""
Tests the loading of data from a flat file.

================================
How to run (from project root):
================================
>> python -m pytest tests/ErgoAnalytics/RawData/test_load_flat_file.py

@ author Jesper Kristensen
Copyright Iterate Labs, Inc. 2018-
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import os
import pandas as pd
from ergo_analytics.data_raw import LoadDataFromLocalDisk
from constants import DATA_FORMAT_CODES


def test_base_data():

    datadisk = LoadDataFromLocalDisk()

    # let's create some fake data:
    some_data = [
        ["2019-01-01", 1.0, 4.0, 6.0],
        ["2019-01-02", 8.0, 6.0, 8.0],
        ["2019-01-04", 12.0, 1.0, 2.0],
        ["2019-01-08", 21.0, 2.0, 1.0],
    ]
    some_names = ["time", "dyaw", "dpitch", "droll"]
    fake_data = pd.DataFrame(data=some_data, columns=some_names)
    # ^^ 3x4 matrix

    # store to disk for now:
    fake_data.to_csv("fake_data.csv")

    # now use BSAFE's raw data parser to load in the data:
    data = datadisk._read_datafile(path="fake_data.csv", data_format_code="4")

    # did we get the data we expect?

    # treat date values differently due to datetime datatype:
    # - convert back to strings we can compare:
    date_values_after_load = list(
        map(lambda x: str(x).split("T")[0], data["Date-Time"].values)
    )

    assert date_values_after_load == list(map(str, fake_data["time"].values))
    assert list(data["DeltaYaw"].values) == list(map(float, fake_data["dyaw"].values))
    assert list(data["DeltaPitch"].values) == list(
        map(float, fake_data["dpitch"].values)
    )
    assert list(data["DeltaRoll"].values) == list(map(float, fake_data["droll"].values))

    # make sure the column names are what we expect:
    assert list(map(str, data.columns)) == DATA_FORMAT_CODES["4"]["NAMES"]
    assert datadisk.data_column_names == DATA_FORMAT_CODES["4"]["NAMES"]

    # let's clean up the file:
    os.remove("fake_data.csv")
