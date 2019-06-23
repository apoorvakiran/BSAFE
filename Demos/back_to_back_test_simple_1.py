# -*- coding: utf-8 -*-
"""
This code serves as a simple back-to-back test of the code.
This is meant as a "get-started" code.

@ author Jesper Kristensen, Jacob Tyrrell
Copyright 2018-
"""

__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import os
import matplotlib.pyplot as plt
import numpy as np
os.sys.path.append('C:\\Users\\Jacob\\Documents\\Data_Analytics\\Analytics')

from Data import LoadGoogleDrive
from Analytics import Experiments

basepath_structured = "demo-data"  # just some demo data

exps = Experiments(basepath=basepath_structured, is_structured=True,
                   cache_path='demo_cache.pkl', ignore_cache=True)

for exp in exps._experiments:
    # loop over the experiments
    print(exp.name)
    print(exp._metrics._motion)
    print(exp._metrics._posture)
    print(exp._metrics._speed)
