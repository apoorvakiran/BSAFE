# -*- coding: utf-8 -*-
"""
Test the utilities.

@ author Jesper Kristensen
Copyright Iterate Labs, Inc. 2018-
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import os
import sys

# == we start by finding the project root:
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
while not os.path.split(ROOT_DIR)[1] == 'BSAFE':
    ROOT_DIR = os.path.dirname(ROOT_DIR)  # cd ../
sys.path.insert(0, ROOT_DIR)  # now insert into our Python path
# ==

import numpy as np
import pandas as pd
import pytest
from unittest.mock import MagicMock
from ergo_analytics import subsample_data

data_format_code = '5'  # in which format is the data coming to us?

# this is data with 6256 rows
test_data_path = os.path.join(ROOT_DIR, "Demos",
                         "demo-data-stationary",
                         "raw_data.csv")

test_data = pd.read_csv(test_data_path)
test_data.drop("Unnamed: 0", inplace=True, axis=1)


# now what happens when the size index is large enough that we only have
# for 1 subsample but not for 2 (there is some left-over data):
def test_cut_off_data_in_subsample():
    """
    We are requesting more subsamples than we have
    """

    count_num_times = 0
    for data_chunk, _ in subsample_data(data=test_data,
                                        use_subsampling=True,
                                        subsample_size_index=5000,
                                        randomize=False,
                                        number_of_subsamples=2):
        # not enough data to have 2 fully-sized chunks
        assert len(data_chunk) == len(test_data)
        # even though we ask for 5000 the data has >6000, but at that point
        # we just say "return all the data since you are not granular enough
        # to care it seems".
        count_num_times += 1

    assert count_num_times == 1


def test_use_subsampling():
    """
    Test how the subsampling method works.
    """

    # here we should just get all the data back since
    # we are not using subsampling:
    for data_chunk, _ in subsample_data(data=test_data, use_subsampling=False):
        assert len(data_chunk) == len(test_data)
        pd.testing.assert_frame_equal(test_data, data_chunk)

    # still not use subsampling:
    for data_chunk, _ in subsample_data(data=None, use_subsampling=False):
        assert data_chunk is None

    # do use it, but with data that is None:
    for data_chunk, _ in subsample_data(data=None, use_subsampling=True):
        assert data_chunk is None


def test_subsample_size_index():
    """
    Test how the subsampling method works.
    """

    # we are using subsampling, but number of rows requested goes beyond
    # number of incoming rows, so should just return the data:
    for data_chunk, _ in subsample_data(data=test_data, use_subsampling=True,
                                        subsample_size_index=8000,
                                        randomize=False,
                                        number_of_subsamples=1):
        assert len(data_chunk) == len(test_data)
        pd.testing.assert_frame_equal(test_data, data_chunk)

    # try with data that is None:
    for data_chunk, _ in subsample_data(data=None, use_subsampling=True,
                                        subsample_size_index=8000,
                                        randomize=False,
                                        number_of_subsamples=1):
        assert data_chunk is None

    for data_chunk, _ in subsample_data(data=test_data, use_subsampling=True,
                                        subsample_size_index=400,
                                        randomize=False,
                                        number_of_subsamples=1):

        assert 375 < len(data_chunk) < 425

    for data_chunk, _ in subsample_data(data=test_data, use_subsampling=True,
                                        subsample_size_index=100,
                                        randomize=False,
                                        number_of_subsamples=1):

        assert 75 < len(data_chunk) < 125

    for data_chunk, _ in subsample_data(data=test_data, use_subsampling=True,
                                        subsample_size_index=50,
                                        randomize=False,
                                        number_of_subsamples=1):

        assert 45 < len(data_chunk) < 55

    for data_chunk, _ in subsample_data(data=test_data, use_subsampling=True,
                                        subsample_size_index=1,
                                        randomize=False,
                                        number_of_subsamples=1):
        assert len(data_chunk) == 1

    for data_chunk, _ in subsample_data(data=test_data, use_subsampling=True,
                                        subsample_size_index=0,
                                        randomize=False,
                                        number_of_subsamples=1):
        assert len(data_chunk) == 0


@pytest.mark.parametrize("num_times_called", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
def test_number_of_subsamples(num_times_called):
    """
    Test how the subsampling method works.
    """

    # we are using subsampling, but number of rows requested goes beyond
    # number of incoming rows, so should just return the data:
    count_num_times = 0
    non_overlapping = []
    for data_chunk, _ in subsample_data(data=test_data, use_subsampling=True,
                                        subsample_size_index=100,
                                        randomize=False,
                                        number_of_subsamples=num_times_called):
        count_num_times += 1

        if len(data_chunk) > 0:
            non_overlapping.append(list(data_chunk.index))

        if num_times_called == 0:
            assert len(data_chunk) == 0

    assert count_num_times == max(num_times_called, 1)

    # now check that no index is overlapping:
    if len(non_overlapping) > 1:
        for l1 in range(len(non_overlapping) - 1):
            for l2 in range(l1 + 1, len(non_overlapping)):
                assert len(np.intersect1d(l1, l2)) == 0


@pytest.mark.parametrize("number_of_subsamples", [1, 10, 20, 100])
def test_more_subsamples_than_we_have(number_of_subsamples):
    """
    We are requesting more subsamples than we have
    """

    count_num_times = 0
    for data_chunk, _ in subsample_data(data=test_data,
                                        use_subsampling=True,
                                        subsample_size_index=8000,
                                        randomize=False,
                                        number_of_subsamples=2):
        count_num_times += 1
        assert len(data_chunk) == len(test_data)

    assert count_num_times == 1


def test_cut_off_data_in_subsample_2():
    """
    We are requesting more subsamples than we have
    """

    count_num_times = 0
    for data_chunk, _ in subsample_data(data=test_data,
                                        use_subsampling=True,
                                        subsample_size_index=1900,
                                        randomize=False,
                                        number_of_subsamples=1):
        # not enough data to have 2 fully-sized chunks
        assert 1800 < len(data_chunk) < 2100
        # now we ask for 2000 and the data is size +6000 so we should get
        # three chunks
        count_num_times += 1

    assert count_num_times == 1

    count_num_times = 0
    for data_chunk, _ in subsample_data(data=test_data,
                                        use_subsampling=True,
                                        subsample_size_index=1900,
                                        randomize=False,
                                        number_of_subsamples=2):

        # not enough data to have 2 fully-sized chunks
        assert 1800 < len(data_chunk) < 2100
        # now we ask for 2000 and the data is size +6000 so we should get
        # three chunks
        count_num_times += 1

    assert count_num_times == 2

    count_num_times = 0
    for data_chunk, _ in subsample_data(data=test_data,
                                        use_subsampling=True,
                                        subsample_size_index=1900,
                                        randomize=False,
                                        number_of_subsamples=3):

        # not enough data to have 2 fully-sized chunks
        assert 1800 < len(data_chunk) < 2100
        # now we ask for 2000 and the data is size +6000 so we should get
        # three chunks
        count_num_times += 1

    assert count_num_times == 3


def test_subsample_size_1_many_subsamples():
    """
    Pick a large number of single-element items.
    """
    indices_we_have_seen = set()

    count_num_times = 0
    for data_chunk, _ in subsample_data(data=test_data,
                                        use_subsampling=True,
                                        subsample_size_index=1,
                                        randomize=False,
                                        number_of_subsamples=4000):

        assert len(data_chunk) == 1

        this_index = list(data_chunk.index)[0]
        assert this_index not in indices_we_have_seen

        indices_we_have_seen.add(list(data_chunk.index)[0])

        count_num_times += 1

    assert count_num_times == 4000


def test_subsample_size_2_many_subsamples():
    """
    Pick a large number of single-element items.
    """
    indices_we_have_seen = set()

    count_num_times = 0
    for data_chunk, _ in subsample_data(data=test_data,
                                        use_subsampling=True,
                                        subsample_size_index=2,
                                        randomize=False,
                                        number_of_subsamples=2000):

        assert len(data_chunk) == 2

        this_index1 = list(data_chunk.index)[0]
        this_index2 = list(data_chunk.index)[1]
        assert this_index1 not in indices_we_have_seen
        assert this_index2 not in indices_we_have_seen

        indices_we_have_seen.add(this_index1)
        indices_we_have_seen.add(this_index2)

        count_num_times += 1

    assert count_num_times == 2000


def test_subsample_randomize():

    indices_seen = set()
    count_num_times = 0
    for data_chunk, _ in subsample_data(data=test_data,
                                        use_subsampling=True,
                                        subsample_size_index=1,
                                        randomize=True,
                                        number_of_subsamples=100):
        assert len(data_chunk) == 1
        this_index = list(data_chunk.index)[0]
        assert this_index not in indices_seen
        indices_seen.add(this_index)
