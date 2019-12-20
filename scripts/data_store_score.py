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

import sys
import pandas as pd
from ergo_analytics.data_raw import LoadDataStore
from ergo_analytics import DataFilterPipeline
from ergo_analytics.filters import FixDateOscillations
from ergo_analytics.filters import DataCentering
from ergo_analytics.filters import ConstructDeltaValues
from ergo_analytics.filters import ZeroShiftFilter
from ergo_analytics.filters import WindowOfRelevantDataFilter
from ergo_analytics.filters import DataImputationFilter
from ergo_analytics.filters import QuadrantFilter
from ergo_analytics import ErgoMetrics


if __name__ == '__main__':
    
    # parse command line:
    if not len(sys.argv) == 3:
        raise Exception("Usage: dscore <tester> <project>")
    
    # parse the user input - selecting which tester and project to use:
    tester = sys.argv[1]
    project = sys.argv[2]

    ds = LoadDataStore()
    raw_df = ds.load(tester=tester, project=project)

    raw_df.dropna(how='all', inplace=True)

    # make some conversions:
    raw_df.iloc[:, 0] = pd.to_datetime(raw_df.iloc[:, 0])
    for j in range(1, 6 + 1):
        raw_df.iloc[:, j] = raw_df.iloc[:, j].astype(float)

    pipeline = DataFilterPipeline()
    # instantiate the filters:
    pipeline.add_filter(name='fix_osc', filter=FixDateOscillations())
    pipeline.add_filter(name='centering1', filter=DataCentering())
    pipeline.add_filter(name='delta_values', filter=ConstructDeltaValues())
    pipeline.add_filter(name='centering2', filter=DataCentering())
    pipeline.add_filter(name='zero_shift_filter', filter=ZeroShiftFilter())
    pipeline.add_filter(name='window', filter=WindowOfRelevantDataFilter())
    pipeline.add_filter(name='impute', filter=DataImputationFilter())
    pipeline.add_filter(name='quadrant_fix', filter=QuadrantFilter())
    # run the pipeline!
    structured_data_chunks = pipeline.run(on_raw_data=raw_df,
                                          with_format_code='5',
                                          use_subsampling=False)

    metrics = ErgoMetrics(list_of_structured_data_chunks=structured_data_chunks)
    metrics.compute()
    score = metrics.get_score()

    print("*" * 12)
    print("The ErgoMetrics score is:")
    print(score)
    print("*" * 12)
