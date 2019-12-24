"""
Quick converter for the original data to turn it into "delta only"
data.

@author Jesper Kristensen
Copyright Iterate Labs, Inc.
"""

import os
import pandas as pd
from constants import DATA_FORMAT_CODES

# ======= USER INPUT ===
code = 5  # which data format code to generate? Example: "code = 4"
number_of_datapoints_in_small_version = 100
# ======================

# NO NEED TO TOUCH CODE BELOW UNLESS YOU KNOW WHAT YOU'RE DOING

data = pd.read_csv('Demos/base_data.csv', header=None)

names = DATA_FORMAT_CODES[f'{code}']['NAMES']
data = data.iloc[:, :len(names)]  # need 6 columns
data.columns = names

dir_name = os.path.join('Demos', f'demo-format-{code}')
if not os.path.isdir(dir_name):
    os.mkdir(dir_name)

final_path = os.path.join(dir_name, 'data.csv')
final_path_small = os.path.join(dir_name, f'data_small.csv')

# store in all-data and "small data" versions:
data.to_csv(final_path, index=False)
data = data.iloc[:number_of_datapoints_in_small_version, :]
data.to_csv(final_path_small, index=False)

