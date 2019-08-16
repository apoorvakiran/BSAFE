# -*- coding: utf-8 -*-
"""
This file handles data loading from Elastic Search.

@ author Jesper Kristensen
Copyright 2018-
"""

__all__ = ["LoadElasticSearch"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

from . import BaseData


class LoadElasticSearch(BaseData):

    def __init__(self):

        super().__init__()

        print("Data loading with Elastic Search object created!")

