# -*- coding: utf-8 -*-
"""
This is a simple system (end-to-end) going from raw data all the way
through reporting. This code also serves as a "get started"
for newcomers to BSAFE.

@ author Jesper Kristensen
Copyright Iterate Labs Inc. 2018-
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import os
import sys

from ergo_analytics.data_raw import LoadDataFromLocalDisk
from ergo_analytics import DataFilterPipeline
from ergo_analytics import ErgoMetrics
from ergo_analytics import ErgoReport
from ergo_analytics.filters import FixDateOscillations
from ergo_analytics.filters import DataCentering
from ergo_analytics.filters import ConstructDeltaValues
from ergo_analytics.filters import WindowOfRelevantDataFilter
from ergo_analytics.filters import DataImputationFilter
from ergo_analytics.filters import QuadrantFilter
from constants import DATA_FORMAT_CODES

data_format_code = '5'  # in which format is the data coming to us?

ROOT_DIR = os.path.absdir(os.path.expanduser("."))
basepath_raw_data = os.path.join(ROOT_DIR, "Demos",
                                 "demo-data-stationary",
                                 "raw_data.csv")

assert os.path.isfile(basepath_raw_data)

put_structured_data_here = os.path.join(ROOT_DIR, "tests", "system")

raw_data_loader = LoadDataFromLocalDisk()
raw_data = raw_data_loader.get_data(path=basepath_raw_data,
                                    destination=put_structured_data_here,
                                    data_format_code=data_format_code)

# now pass the raw data through our data filter pipeline:
pipeline = DataFilterPipeline()
# instantiate the filters:
# pipeline.add_filter(name='fix_osc', filter=FixDateOscillations())
# pipeline.add_filter(name='centering1', filter=DataCentering())
pipeline.add_filter(name='delta_values', filter=ConstructDeltaValues())
# pipeline.add_filter(name='centering2', filter=DataCentering())
# pipeline.add_filter(name='window', filter=WindowOfRelevantDataFilter())
# pipeline.add_filter(name='impute', filter=DataImputationFilter())
# pipeline.add_filter(name='quadrant_fix', filter=QuadrantFilter())

# run the pipeline!
structured_data = pipeline.run(on_raw_data=raw_data,
                               with_format_code=data_format_code,
                               is_sorted=True, use_subsampling=True,
                               number_of_subsamples=2,
                               subsample_size_index=100,
                               randomize_subsampling=False)


def filter_zero_line_shifts(yaw=None):
    
    # import matplotlib.pyplot as plt
    # plt.figure(1)
    # yaw = structured_data.get_data(type='yaw', loc='delta')
    # yaw.plot(legend='yaw')
    # pitch = structured_data.get_data(type='pitch', loc='delta')
    # pitch.plot(legend='pitch')
    # roll = structured_data.get_data(type='roll', loc='delta')
    # roll.plot(legend='roll')
    #
    # plt.legend()

    import numpy as np
    dyaw = np.absolute(np.gradient(yaw))
    dyaw = np.clip(dyaw, a_min=0, a_max=None)

    q = 0
    percentile_to_use = np.percentile(dyaw, q=q)
    while percentile_to_use < 1e-10:
        q += 1  # 1 percentage-point at a time
        percentile_to_use = np.percentile(dyaw, q=q)
    print(f"Using the {q}th percentile to shift data up by before log.")

    dyaw += percentile_to_use  # make sure we can take the log
    dyaw = np.log(dyaw)

    # plt.figure(2)
    # plt.subplot(211)
    # # plt.plot(dyaw, label='dyaw')
    # plt.axhline(0, linestyle='-', color='k')
    # plt.subplot(212)
    # # plt.hist(dyaw, bins=100)
    # plt.plot(yaw, label='yaw')

    # shift happens(!) - but where?
    shift_indices = list(np.where(dyaw > 0)[0])  # here

    # if len(shift_indices) == 0:
    #     return

    # first mean - has to be gotten from calibration:
    first_mean = yaw.iloc[0]
    yaw.iloc[:shift_indices[0]] -= first_mean

    for j in range(len(shift_indices[1:])):
        the_new_zeroline = yaw[shift_indices[j]]
        yaw.iloc[shift_indices[j]:shift_indices[j + 1]] -= the_new_zeroline

    # comes also from calibration:
    final_zero_line = yaw.iloc[-1]
    yaw[shift_indices[-1]:] -= final_zero_line

    # plt.subplot(211)
    # plt.plot(yaw, label='corrected')
    #
    # plt.legend()
    # plt.show()

    return yaw

yaw = filter_zero_line_shifts(structured_data.get_data(type='yaw', loc='delta'))
pitch = filter_zero_line_shifts(structured_data.get_data(type='pitch', loc='delta'))
roll = filter_zero_line_shifts(structured_data.get_data(type='roll', loc='delta'))

import matplotlib.pyplot as plt
plt.figure(1)
plt.plot(yaw, label='yaw')
plt.plot(pitch, label='pitch')
plt.plot(roll, label='roll')
plt.legend()
plt.show()

structured_data._yaw['delta'] = yaw
structured_data._yaw['pitch'] = pitch
structured_data._yaw['roll'] = roll

metrics = ErgoMetrics(structured_data=structured_data)
metrics.compute()

report = ErgoReport(ergo_metrics=metrics, mac_address='something')

print(report.to_string())
