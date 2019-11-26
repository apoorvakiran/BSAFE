# -*- coding: utf-8 -*-
"""
Load data from Iterate Labs' Data Store.

@ author Jesper Kristensen
Copyright 2018-
"""

__all__ = ["LoadDataStore"]
__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import logging
from . import BaseData

logger = logging.getLogger()


class LoadDataStore(BaseData):
    """
    Loads data from Iterate Labs' Data Store.
    """

    def __init__(self):

        super().__init__()

        logger.info("Data loading from Data Store object created!")

    def load(self, project_id=None, file_nickname=None):
        """
        Loads all data from the project ID. If file_nickname is given load
        only that file from the specific project ID.
        """

        from scripts import data_store

        import pdb
        pdb.set_trace()
