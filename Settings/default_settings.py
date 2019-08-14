"""
This file contains various settings for the overall code all
collected in one place.

For example, it contains hard-coded names for the data being loaded.
Or it contains hard-coded names for the analyses conducted which is
communicated between SAFE and AWS.

The point is to keep all these rarely-of-ever changing variables in one place.

Iterate Labs, Co.
Copyright 2018-
"""

__author__ = "Iterate Labs, Co."
__version__ = "Alpha"

# ==== DATA LOADING ====
COLUMN_NAMES_FORMAT_1 = ['Date-Time', 'Yaw[0](deg)', 'Pitch[0](deg)',
                         'Roll[0](deg)', 'Yaw[1](deg)', 'Pitch[1](deg)',
                         'Roll[1](deg)', 'DeltaYaw', 'DeltaPitch', 'DeltaRoll']


COLUMN_NAMES_FORMAT_2 = ["Date-Time", "ax[0](mg)", "ay[0](mg)", "az[0](mg)",
                         "gx[0](dps)", "gy[0](dps)", "gz[0](dps)", "mx[0](uT)",
                         "my[0](uT)", "mz[0](uT)", "Yaw[0](deg)",
                         "Pitch[0](deg)", "Roll[0](deg)", "ax[1](mg)",
                         "ay[1](mg)", "az[1](mg)", "gx[1](dps)", "gy[1](dps)",
                         "gz[1](dps)", "mx[1](uT)", "my[1](uT)", "mz[1](uT)",
                         "Yaw[1](deg)", "Pitch[1](deg)", "Roll[1](deg)"]

# when loading data, we allow that, say, 30% is missing/not useful:
FRACTION_OF_DATA_USEFUL = 0.7
# ====
