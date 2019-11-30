# -*- coding: utf-8 -*-
"""
Load data from Iterate Labs' Data Storage.

@ author Jesper Kristensen
Copyright 2018-
"""

__all__ = ["LoadDataStorage"]
__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import os
import sys

# == we start by finding the project root:
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
while not os.path.split(ROOT_DIR)[1] == 'BSAFE':
    ROOT_DIR = os.path.dirname(ROOT_DIR)  # cd ../
sys.path.insert(0, ROOT_DIR)  # now insert into our Python path
sys.path.insert(0, os.path.join(ROOT_DIR, 'scripts'))
# ==

import logging

from tempfile import mkdtemp
import subprocess
from . import BaseData

logger = logging.getLogger()


class LoadDataStorage(BaseData):
    """
    Loads data from Iterate Labs' Data Storage.
    """

    def __init__(self):

        super().__init__()

        logger.info("Data loading from Data Storage object created!")

    def load(self, project_id=None, file_nickname=None):
        """
        Loads all data from the project ID. If file_nickname is given load
        only that file from the specific project ID.
        """

        tmp_dir = mkdtemp()

        result = subprocess.check_output(
            [f'pipenv run python scripts/data_storage.py '
             f'--download-all-files {project_id} {tmp_dir}'],
            shell=True)

        # call the data_storage script:

        # 1) Parse the "result" to get all file names.
        # 2) Load all files and create iterator over the data (lazy iterator).s
        # 3) return that iterator.



        import pdb
        pdb.set_trace()
