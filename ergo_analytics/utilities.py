# -*- coding: utf-8 -*-
"""
Contains utilities for ErgoAnalytics.

@ author Jesper Kristensen
Copyright 2018 Iterate Labs, Inc.
"""

__all__ = ["is_numeric", "digitize_values", "rad_to_deg"]
__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

from numpy import abs
from numpy import digitize
from numpy import degrees


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
