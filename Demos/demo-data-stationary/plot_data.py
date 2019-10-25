# -*- coding: utf-8 -*-
"""
Quickly plot data.

@ author Jesper Kristensen
Copyright 2018-
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('raw_data.csv')
data = data.drop('Unnamed: 0', axis=1)

data.plot()
plt.show()
# now look at the figure that opens!
