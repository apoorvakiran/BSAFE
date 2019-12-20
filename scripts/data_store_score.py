# -*- coding: utf-8 -*-
"""
This script computes the score for the latest file
for a given tester and project from Iterate Lab's Data Store.

This is called with "dscore":
    >> "dscore <tester> <project>"

@ author Jesper Kristensen
Iterate Labs Inc. Copyright 2018-
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import os
import sys
import matplotlib.pyplot as plt
from ergo_analytics.data_raw import LoadDataStore


if __name__ == '__main__':
    
    # parse command line:
    if not len(sys.argv) == 3:
        raise Exception("Usage: dscore <tester> <project>")
    
    # parse the user input - selecting which tester and project to use:
    tester = sys.argv[1]
    project = sys.argv[2]

    ds = LoadDataStore()
    raw_df = ds.load(tester=tester, project=project)
    
    # NOW SCORE IT (TEST THAT PART FIRST)...
    print("TODO!!!")

