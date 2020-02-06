# -*- coding: utf-8 -*-
"""Here we introduce a set of Ergo Metric scores.

The scores determine the overall ergonomic quality and
risk of injury and thus play a central role to our analytic. The scores
can also be used to indicate productivity.

@ author Jesper Kristensen
Copyright 2018 Iterate Labs, Inc.
All Rights Reserved.
"""

__author__ = "Jesper Kristensen"
__version__ = "Alpha"

from .common import *
from ._angular_binning import angular_binning
from .base import *
# import scores
from .activity import *
from .posture import *
