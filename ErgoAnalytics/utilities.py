# -*- coding: utf-8 -*-
"""

@ author Jesper Kristensen
Copyright 2018-
"""

__all__ = ["is_numeric"]
__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"


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
