# -*- coding: utf-8 -*-
"""
Contains utilities for ErgoAnalytics.

@ author Jesper Kristensen
Copyright 2018 Iterate Labs, Inc.
"""

__all__ = ["is_numeric", "digitize_values", "rad_to_deg", "subsample_data"]
__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import logging
from numpy import abs
from numpy import digitize
from numpy import degrees
from numpy import array_split
from numpy import arange
from numpy import median
from numpy import where
from numpy.random import choice

logger = logging.getLogger()


def subsample_data(data=None, number_of_subsamples=100,
                   use_subsampling=True,
                   subsample_size_index=1000, randomize=True,
                   **kwargs):
    """
    This is a utility which can create chunks of data in various useful
    formats including support for randomization.

    Given incoming "data" as a dataframe, can break that
    data into "number_of_subsamples" subsamples each of
    size "subsample_size_index".

    This is an iterator which will return the chunks of data subsamples.
    """

    if data is None:
        yield None, dict()
        return

    if subsample_size_index == 0 or number_of_subsamples == 0:
        yield [], dict()
        return

    if not use_subsampling or data is None:
        chunk_info = dict()
        yield data, chunk_info
        return


    if not randomize:

        # generate all chunks:
        num_chunks_target = max(len(data) // subsample_size_index, 1)
        all_chunks = array_split(data, num_chunks_target)
        num_chunks = len(all_chunks)

        logger.debug(
            f"Splitting data into {num_chunks} chunks! "
            f"(requested: {num_chunks_target})")

        # at this point, we have less chunks requested than we split the
        # data into, so now we need to evenly return a set of "num_chunks"
        # chunks. We can do this by leveraging KFold from scikit-learn
        # but just operate on indices:
        chunk_indices = arange(num_chunks)

        for ixs in array_split(chunk_indices, number_of_subsamples):
            if len(ixs) == 0:
                return
            ix = int(median(ixs))
            yield all_chunks[ix], dict()

    else:
        # we do randomize the chunks returned:

        # so just keep generating index sets:
        # draw a random number in the range [0, len(data) - sample_size]:

        valid_start_indices = arange(len(data))
        valid_start_indices = valid_start_indices[:where(valid_start_indices ==
                                    len(data) - subsample_size_index)[0][0]]

        random_start_indices = choice(valid_start_indices,
                                      size=number_of_subsamples, replace=False)

        for ix in random_start_indices:
            yield data.iloc[ix:ix + subsample_size_index], dict()


def is_numeric(val):
    """
    Check that a value is numeric.

    :param val:
    :return:
    """
    try:
        float(val)
        return True
    except Exception:
        return False


def digitize_values(values=None, bins=None):
    """
    Digitizes a set of values into the bins given.

    :param values:
    :param bins:
    :return:
    """
    values_dig = digitize(abs(values), bins, right=True)  # include end points
    tmp = [0] * len(bins)

    for val in values_dig:
        # 15, 30, 45, ...
        tmp[val] += 1

    return tmp


def rad_to_deg(data=None):
    """
    Converts dataframe of radians to degrees.

    :param data: incoming data with values in radians.
    :return: data with values converted to degrees.
    """
    return degrees(data)
