# -*- coding: utf-8 -*-
"""
This is the first test to run.

This code serves as a simple back-to-back test of the code.
This is meant as a "get-started" code.

@ author Jesper Kristensen
Copyright Iterate Labs Inc. 2018-
"""

__author__ = "Jesper Kristensen"
__version__ = "Alpha"

from Analytics import Experiments, Metrics

basepath_structured = "demo-data"  # just some demo data

exps = Experiments(basepath=basepath_structured, is_structured=True, ignore_cache=True)

for exp in exps.experiments():
    # loop over individual experiments

    mets = Metrics(experiment_obj=exp)
    
    print(exp.name)

    print(mets.motion)
    print(mets.posture)
    print(mets.speed)
