# -*- coding: utf-8 -*-
"""
Test Iterate Lab Inc.'s Data Storage.

@ author Jesper Kristensen
Copyright 2018-
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

from ergo_analytics.data_raw import LoadDataStore


def test_load_data_storage_basic():
    """
    Very basic test that the connections work to AWS etc.

    :return:
    """

    ds = LoadDataStore()
    raw_df = ds.load(tester='john', project='johnson')

    assert len(raw_df) == 1750
