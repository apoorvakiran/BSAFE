# -*- coding: utf-8 -*-
"""
The idea of having a "Raw Data" module is to pay special attention to the data
collection, cleaning, and standardization. This really forms the backbone of
everything that follows (metrics, reporting, etc.).

@ author Jesper Kristensen
Copyright 2018
"""

__author__ = "Jesper Kristensen"
__version__ = "Alpha"

from .base_data import *
from .arduino_data import *
from .load_flat_file import *
from .load_google_drive import *
from .load_aws_s3 import *
from .load_elastic_search import *
