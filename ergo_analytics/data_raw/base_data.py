# -*- coding: utf-8 -*-
"""
Here we share some basic data interface across all our data parser classes.
For example, we have a "static" data loader and a "streaming" data loader.
These both share some commonalities captured here.

@ author Jesper Kristensen
Copyright 2018
"""

__all__ = ["BaseData"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import os
import s3fs
from pyathena import connect
import yaml
import numpy as np
import pandas as pd
from constants import *
from constants import DATA_FORMAT_CODES
import logging

logger = logging.getLogger()
try:
    with open("settings.yml", "r") as fd:
        config = yaml.load(fd, yaml.SafeLoader)
except FileNotFoundError:
    logger.warning("Could not find the 'settings.yml' file in the repo root!")
    config = dict()


class BaseData(object):

    _data_column_names = None  # name of columns in the data
    _number_of_points = None
    _data_format_code = None

    def __init__(self):
        pass

    @property
    def data_format_code(self):
        return self._data_format_code

    @property
    def data_column_names(self):
        return self._data_column_names

    @property
    def number_of_points(self):
        return self._number_of_points

    @staticmethod
    def _find_data_format_code(path=None):
        """Find correct data format codes to load data from path."""

        loaded = False
        found = False
        lcols = None
        dfc = None
        for dfc in DATA_FORMAT_CODES:
            these_names = DATA_FORMAT_CODES[dfc]["NAMES"]

            if not loaded:
                lcols = len(pd.read_csv(path).columns)
                loaded = True

            if lcols == len(these_names):
                found = True
                break

        if not found or dfc is None:
            raise Exception("The data format code could not found for the data!")

        return dfc

    def _cast_to_correct_types(self, all_data=None, data_format_code=None):
        """
        Makes sure the data is in the format expected from its streaming type.

        :param all_data: pd.DataFrame containing data.
        :param data_format_code: what is the streaming type of data?
        :return:
        """
        if all_data is None:
            msg = "Please provide valid data!"
            logger.exception(msg)
            raise Exception(msg)

        # now convert data based on the types we know:
        data_column_names = DATA_FORMAT_CODES[data_format_code]["NAMES"]
        data_column_types = DATA_FORMAT_CODES[data_format_code]["TYPES"]

        conv = dict(zip(data_column_names, data_column_types))
        all_data = all_data.apply(conv)

        # make sure index is ints (can convert to "float64" if there are
        # some NaNs here and there):
        all_data.index = list(map(int, all_data.index))

        self._number_of_points = len(all_data)

        return all_data

    def retrieve_any_macaddress_with_data(
        self,
        at_least_this_much_data_in_total=50,
        return_max_this_much_data=20,
        force_rerun=False,
    ):
        """Used initially for /status endpoint: Get _any_ mac address with data for testing BSAFE.

        The mac address can then be used in a later query to retrieve data for testing.

        Returns:
            Wearable mac address (string): Some device mac address (any with data).
            Data (pd DataFrame): Data of the corresponding mac address.
        """
        # Start by just reading from S3 (no more than 1 month old data there due to lifecyclke policy)
        s3_query_bucket = config["athena_query_dir"]

        fs = s3fs.S3FileSystem(
            key=os.getenv("BSAFE_AWS_ACCESS_KEY", "AWS_ACCESS_KEY"),
            secret=os.getenv("BSAFE_AWS_SECRET_KEY", "AWS_SECRET_KEY"),
        )
        _file = None
        for _file in fs.ls(s3_query_bucket):
            if _file.endswith(".csv"):
                break
        need_cache_bust = _file is None

        if not need_cache_bust and not force_rerun:
            logger.debug("Cache hit on Athena query")
            # cache hit
            with fs.open(_file, "r") as fd:
                df = pd.read_csv(fd)
        else:
            logger.debug("Re-generating Athena query")
            # re-query Athena (should happen once per month)
            # Get all data from a/any device with more than 50 data point

            athena_database_name = config.get("athena_database_name")
            athena_table_name = config.get("athena_table_name")
            conn = connect(
                aws_access_key_id=os.getenv("BSAFE_AWS_ACCESS_KEY", "AWS_ACCESS_KEY"),
                aws_secret_access_key=os.getenv(
                    "BSAFE_AWS_SECRET_KEY", "AWS_SECRET_KEY"
                ),
                s3_staging_dir="s3://" + config["athena_query_dir"] + "/",
                region_name="us-east-1",
                work_group=config["athena_workgroup"],
            )
            df = pd.read_sql(
                """SELECT *
                              FROM "{}"."{}"
                              WHERE device = (SELECT device
                                              FROM "{}"."{}"
                                              GROUP BY device
                                              HAVING count(*) > {}
                                              LIMIT 1)
                              LIMIT {};""".format(
                    athena_database_name,
                    athena_table_name,
                    athena_database_name,
                    athena_table_name,
                    at_least_this_much_data_in_total,
                    return_max_this_much_data,
                ),
                conn,
            )

        format_code_found = False
        names = None  # will be set first iteration
        the_code = None
        all_data = []
        for row in df.itertuples():
            this_data = np.r_[
                pd.to_datetime(row.wearable_timestamp), row.value.split(",")
            ]

            if not format_code_found:
                the_code = None
                for code in DATA_FORMAT_CODES:
                    names = DATA_FORMAT_CODES[code]["NAMES"]
                    if len(names) == len(this_data):
                        the_code = code
                        break
                if the_code is None:
                    raise Exception("Data is in unknown format!")
                format_code_found = True

            this_df = pd.DataFrame(data=[this_data], columns=names)
            all_data.append(this_df)

        this_mac = df.iloc[0].device
        raw_data = pd.concat(all_data)

        self._data_format_code = the_code

        raw_data = self._cast_to_correct_types(
            all_data=raw_data, data_format_code=self._data_format_code
        )

        raw_data.sort_values("Date-Time", inplace=True)

        return this_mac, raw_data
