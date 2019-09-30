"""
This file contains various settings for the overall code all
collected in one place.

*For example* it contains hard-coded names for the data being loaded.
Or it contains hard-coded names for the analyses conducted which is
communicated between SAFE and AWS.

The point is to keep all these rarely-of-ever changing variables in one place
and reference them from here.

Iterate Labs, Co.
Copyright 2018-
"""

__all__ = ['DATA_FORMAT_CODES', "FRACTION_OF_DATA_USEFUL"]
__copyright__ = "Iterate Labs, Co., 2018-"
__author__ = "Iterate Labs, Co."
__version__ = "Alpha"

# ==== TOPIC: DATA LOADING ====
# *NOTE* If adding or removing any "column_names_format_j" you need to update
# the dict-variable "DATA_FORMAT_CODES" further down as well

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

COLUMN_NAMES_FORMAT_3 = """Date-Time
ax[0]
      ay[0]
     az[0]
    ax[1]
     ay[1]
   az[1]
      Gx[0],
      Gy[0],
      Gz[0],
      Gx[1],
      Gy[1],
      Gz[1],
      (int)Mx[0]
      (int)My[0]
      (int)Mz[0]
      (int)Mx[1]
      (int)My[1]
      (int)Mz[1]
      q[0][0]
      q[0][1]
      q[0][2]
      q[0][3]
      q[1][0]
      q[1][1]
      q[1][2]
      q[1][3]
      yaw[0],
      pitch[0],
      roll[0],
      yaw[1],
      pitch[1],
      roll[1],
      delta_yaw,
      delta_pitch,
      delta_roll""".split()
COLUMN_NAMES_FORMAT_3 = list(map(lambda x: x.strip().rstrip(',').lstrip(','),
                                 COLUMN_NAMES_FORMAT_3))

# bluetooth capabilities limit amount of data that can be transferred:
COLUMN_NAMES_FORMAT_4 = ['Date-Time', 'DeltaYaw', 'DeltaPitch', 'DeltaRoll']

# *DO NOT DELETE*
# when loading data, we allow that, say, 30% is missing/not useful:
FRACTION_OF_DATA_USEFUL = 0.7  # prevent too much missing data for the analysis

# *DO NOT DELETE VARIABLE; BUT CHANGE AS PER INSTRUCTIONS ABOVE*
# here we collect all the data format codes into an easy-to-access dictionary
# that can be accessed programmatically later on - as this grows (if it does)
# we can turn this into a database like postgres or similar:
DATA_FORMAT_CODES = {"1": COLUMN_NAMES_FORMAT_1,
                     "2": COLUMN_NAMES_FORMAT_2,
                     "3": COLUMN_NAMES_FORMAT_3,
                     "4": COLUMN_NAMES_FORMAT_4}
# ====
