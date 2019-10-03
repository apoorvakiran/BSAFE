# -*- coding: utf-8 -*-
"""
This is the first test to run when making code changes.
This code is supposed to be the bare minimum bar to clear - it needs to
succesfully finish.

This code serves as a simple back-to-back test of the code.
This is meant as a "get-started" code.

@ author Jesper Kristensen
Copyright Iterate Labs Inc. 2018-
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

from ErgoAnalytics import CollectionStructuredData
from ErgoAnalytics import ErgoMetrics

# ==== some tests to run:
# basepath_structured = "Demos/demo-data"  # just some demo data for testing
# data_format_code = '2'
#
basepath_structured = "../../Demos/demo-data-only-deltas"
data_format_code = '4'
# ==========================

msd = CollectionStructuredData(basepath=basepath_structured,
                               is_cataloged=True, ignore_cache=True,
                               data_format_code=data_format_code)

for structured_data in msd.datasets():
    # loop over individual structured data objects

    mets = ErgoMetrics(collection_structured_data_obj=structured_data)

    # just print some things for testing purposes
    # TODO: Make these actual checks in pytest...
    print(structured_data.name)

    print(mets.posture)
    print(mets.speed)

# [0.0, 0.0, 7.0, 7.0]
# [41.59958134606569, 139.6475497017071, 110.68980916739281]