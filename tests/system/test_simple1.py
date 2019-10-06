# -*- coding: utf-8 -*-
"""
<<<<<<< HEAD
This is a simple system (end-to-end) going from raw data all the way
through reporting.

This code also serves as a "get started" for newcomers to BSAFE.
=======
This is the first test to run when making code changes.
This code is supposed to be the bare minimum bar to clear - it needs to
succesfully finish.

This code serves as a simple back-to-back test of the code.
This is meant as a "get-started" code.
>>>>>>> 9dd757a67b391ef2c5ce87dce644140871f4bf8e

@ author Jesper Kristensen
Copyright Iterate Labs Inc. 2018-
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

<<<<<<< HEAD
import os
import sys

# == we start by finding the project root:
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
while not os.path.split(ROOT_DIR)[1] == 'BSAFE':
    ROOT_DIR = os.path.dirname(ROOT_DIR)  # cd ../
sys.path.insert(0, ROOT_DIR)  # now insert into our Python path
# ==

from ErgoAnalytics.Data_Raw import LoadDataFromLocalDisk
from ErgoAnalytics import DataFilterPipeline
from ErgoAnalytics import ErgoMetrics


basepath_raw_data = os.path.join(ROOT_DIR,
                                 "tests/system/Fixtures/demo-data-only-deltas",
                                 "data_example1.csv")
data_format_code = '4'  # in which format is the data coming to us?

assert os.path.isfile(basepath_raw_data)

put_structured_data_here = os.path.join(ROOT_DIR, "tests", "system")

raw_data_loader = LoadDataFromLocalDisk()
raw_data = raw_data_loader.get_data(path=basepath_raw_data,
                                    destination=put_structured_data_here,
                                    data_format_code=data_format_code)

# now pass the raw data through our data filter pipeline:
pipeline = DataFilterPipeline()
structured_data = pipeline.run(raw_data=raw_data)

metrics = ErgoMetrics(structured_data=structured_data)
metrics.compute()

print(structured_data.name)
print(metrics.get_score(name='posture'))
print(metrics.get_score(name='speed'))
=======
from ErgoAnalytics import CollectionStructuredData
from ErgoAnalytics import ErgoMetrics

# # ==== some tests to run:
# # basepath_structured = "Demos/demo-data"  # just some demo data for testing
# # data_format_code = '2'
# #
# basepath_structured = "Demos/demo-data-only-deltas"
# data_format_code = '4'
# # ==========================

# msd = CollectionStructuredData(basepath=basepath_structured,
#                                is_cataloged=True, ignore_cache=True,
#                                data_format_code=data_format_code)

# for structured_data in msd.datasets():
#     # loop over individual structured data objects

#     mets = ErgoMetrics(collection_structured_data_obj=structured_data)

#     # just print some things for testing purposes
#     # TODO: Make these actual checks in pytest...
#     print(structured_data.name)

#     print(mets.posture)
#     print(mets.speed)

# # [0.0, 0.0, 7.0, 7.0]
# # [41.59958134606569, 139.6475497017071, 110.68980916739281]
>>>>>>> 9dd757a67b391ef2c5ce87dce644140871f4bf8e
