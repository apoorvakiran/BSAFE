# -*- coding: utf-8 -*-
"""
This is an ETL pipeline that takes in raw data, applies pre-processing and
various transformations and outputs structured data.

@ author Jesper Kristensen with Iterate Labs, Inc.
Copyright 2018 Iterate Labs, Inc.
"""

__all__ = ["DataFilterPipeline"]
__author__ = "Iterate Labs, Inc."
__version__ = "Alpha"

from copy import deepcopy
import numpy as np
from ergo_analytics.filters import CreateStructuredData
import logging

logger = logging.getLogger()


class DataFilterPipeline(object):
    """
    Pipeline of tasks capabile of taking in a raw data object, applying
    transformations, and outputting a structured data object.

    The pipeline leverages the filters in "Data_Filters".
    """

    _pipeline = None
    _results = None

    def __init__(self):
        """
        Constructs an object from which metrics can be computed
        based off of a "Structured Data" object.

        :param raw_data: the raw data to process
        :param is_streaming: is the data coming in, in a streaming format?
        """

        self._pipeline = dict()  # dict is ordered
        self._results = dict()

    def update_params(self, new_params=None):
        """
        Updates each filter in the pipeline with the incoming parameters.
        This is usefu if there are common parameters between all filters.
        """
        for filter_name in self._pipeline.keys():
            self._pipeline[filter_name].update(new_params=new_params)

    def view(self):
        return self._pipeline

    def add_filter(self, name=None, filter=None):
        """
        Adds a filter to the pipeline.

        :param name: the name of this filter
        :param filter: filter object
        """
        if name in self._pipeline:
            raise Exception(f"Filter by name '{name}' already exists!")

        self._pipeline[name] = filter

    def remove_filter(self, name=None):
        """
        :param name: name (same as used when .add(...) was called)
        of filter to remove.
        """
        if name not in self._pipeline:
            raise Exception(f"The filter '{name}' was not found in "
                            f"the pipeline")

        return self._pipeline.pop(name)

    def update_filter(self, name=None, new_params=None):
        """
        Update existing filter in the pipeline.

        :param name: Which filter to update?
        :param new_params: which parameters to pass to the filter?
        """
        if name not in self._pipeline:
            raise Exception(f"The filter '{name}' was not found in "
                            f"the pipeline")

        if not new_params:
            return

        self._pipeline[name].update(new_params=new_params)

    def run(self, on_raw_data=None, with_format_code='5'):
        """
        Runs the pipeline on incoming raw data.
        Returns structured data.

        :return:
        """
        # make sure the raw data points have unique indices:
        on_raw_data.reset_index(drop=True, inplace=True)

        # make sure to update the data format code:
        self.update_params(new_params=dict(data_format_code=with_format_code))

        initial_columns = list(on_raw_data.columns)

        initial_data = on_raw_data

        all_added_columns = []  # keep track of any additional/derivative data
        all_removed_columns = []

        current_data = on_raw_data.copy()
        for _, filter in self._pipeline.items():
            self._results[filter] = dict()
            current_data, changes = filter.apply(data=current_data)
            self._results[filter]['data'] = current_data
            self._results[filter]['changes'] = changes

            all_added_columns.append(changes.get('added', []))
            all_removed_columns.append(changes.get('removed', []))

        all_added_columns = [item for sublist in all_added_columns for item in
                             sublist]
        all_removed_columns = [item for sublist in all_removed_columns for item
                               in sublist]

        assert len(all_removed_columns) == 0  # NEEDS implementation if >0

        assert current_data.shape[1] == len(list(
            np.unique(list(on_raw_data.columns) + all_added_columns)))

        # now what data remains?
        # first get the indices
        data_post_pipeline = initial_data.iloc[current_data.index, :]
        # now update the data in the columns

        # update the initial data to the "data post pipeline" values:
        for col in initial_columns + all_added_columns:
            data_post_pipeline[col] = current_data[col]

        # sort, drop duplicates, and reset index:
        logger.debug("Dropping duplicate data "
                     "points - currently we have "
                     "{} pts.".format(len(data_post_pipeline)))

        # TODO(JTK): these should be filters
        # data_post_pipeline.sort_values(by=['Date-Time'], ascending=True,
        #                                inplace=True)
        data_post_pipeline.drop_duplicates(subset=['Date-Time'], inplace=True)
        data_post_pipeline.reset_index(drop=True, inplace=True)

        logger.debug("After dropping duplicates we have "
                     "{} pts.".format(len(data_post_pipeline)))

        # always create structured data at the end of the pipeline:
        f_str_data = CreateStructuredData()
        f_str_data.update(new_params=dict(data_format_code='5'))
        structured_data, _ = f_str_data.apply(data=data_post_pipeline)

        logger.debug("Raw data successfully converted to structured data!")

        if structured_data.number_of_points <= 1:
            logger.warning("You only have <=1 data point to analyze!")


        return structured_data

    def get_result(self, name=None):
        return self._results[name]
