# -*- coding: utf-8 -*-
"""Contains utilities for ErgoAnalytics.

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
                   use_subsampling=True, consecutive_subsamples=False,
                   subsample_size_index=1000, randomize=True,
                   exact_chunk_size=True, anchor_data_vs_time=False, **kwargs):
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

    if subsample_size_index is not None:
        subsample_size_index = int(subsample_size_index)

    if number_of_subsamples is not None:
        number_of_subsamples = int(number_of_subsamples)

    if subsample_size_index == 0 or number_of_subsamples == 0:
        yield [], dict()
        return

    if not use_subsampling or data is None:
        chunk_info = dict()
        yield data, chunk_info
        return

    if consecutive_subsamples and randomize:
        msg = "Please select one of consecutive subsamples or random!"
        logger.exception(msg)
        raise Exception(msg)

    if not randomize:

        # generate all chunks:
        num_chunks_target = max(len(data) // subsample_size_index, 1)
        all_chunks = array_split(data, num_chunks_target)
        num_chunks = len(all_chunks)

        logger.debug(
            f"Splitting data into {num_chunks} chunks! "
            f"(requested: {num_chunks_target})")

        if consecutive_subsamples:

            if exact_chunk_size:
                # return as many chunks as we can:
                we_have_data_left = num_chunks > 0
                ix = 0
                while we_have_data_left:

                    # anchor the data to always start at zero?
                    take_from = 0 if anchor_data_vs_time else ix

                    yield data.iloc[take_from:ix + subsample_size_index], dict()
                    ix += subsample_size_index
                    # we need to have at least enough data for the subsample:
                    we_have_data_left = len(data.iloc[ix:ix + subsample_size_index]) >= subsample_size_index
            else:
                # return as many chunks as we can:
                we_have_data_left = len(data) > 0
                ix = 0
                while we_have_data_left:

                    # anchor the data to always start at zero?
                    take_from = 0 if anchor_data_vs_time else ix

                    yield data.iloc[take_from:ix + subsample_size_index], dict()
                    ix += subsample_size_index
                    # any data left is ok
                    we_have_data_left = len(data.iloc[ix:ix + subsample_size_index]) > 0

            return

        # Here: we do not want consecutive chunks, but we want to
        # process every "Nth" chunk (so we skip some chunks):
        # at this point, we have less chunks requested than we split the
        # data into, so now we need to evenly return a set of "num_chunks"
        # chunks. We can do this by leveraging KFold from scikit-learn
        # but just operate on indices:
        chunk_indices = arange(num_chunks)  # index the chunks

        latest_ix = None
        for ixs in array_split(chunk_indices, number_of_subsamples):
            if len(ixs) == 0:
                # if we request a larger susample size than we have data
                # we jut return the same data over and over
                # number_of_subsamples times - so force this to be zero
                # instead of empty:
                ixs = latest_ix if latest_ix is not None else [0]

            ix = int(median(ixs))
            yield all_chunks[ix], dict()
            latest_ix = [ix]

    else:
        # we do randomize the chunks returned:

        # so just keep generating index sets:
        # draw a random number in the range [0, len(data) - sample_size]:

        valid_start_indices = arange(len(data))
        cut_ix = where(valid_start_indices ==
                       len(data) - subsample_size_index)[0]

        if len(cut_ix) > 0:
            cut_ix = cut_ix[0]
            valid_start_indices = valid_start_indices[:cut_ix]
            replace = False
        else:
            # in this case the subsample size is larger than the entire
            # population of data
            valid_start_indices = [0]
            replace = True  # there will have to be overlap

        random_start_indices = choice(valid_start_indices,
                                      size=number_of_subsamples,
                                      replace=replace)

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
