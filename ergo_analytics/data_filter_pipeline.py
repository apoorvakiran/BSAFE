# -*- coding: utf-8 -*-
"""
This is an ETL pipeline that takes in raw data, applies pre-processing and
various transformations and outputs structured data.

@ author Jesper Kristensen with Iterate Labs, Inc.
Copyright 2018 Iterate Labs, Inc.
All Rights Reserved.
"""

__all__ = ["DataFilterPipeline"]
__author__ = "Iterate Labs, Inc."
__version__ = "Alpha"

from copy import deepcopy
import os
import json
import numpy as np
import pandas as pd
import shutil
import matplotlib.pyplot as plt
from ergo_analytics.filters import CreateStructuredData
from ergo_analytics.utilities import subsample_data
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
            # TODO: We should index into the filter here?!
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

    def run(self, on_raw_data=None, with_format_code='5', is_sorted=True,
            use_subsampling=False, number_of_subsamples=10,
            randomize_subsampling=False, consecutive_subsamples=False,
            subsample_size_index=1000, debug=False, debug_folder_prepend=None,
            anchor_data_vs_time=False, **kwargs):
        """
        Run the pipeline on the incoming raw data.
        This is done by splitting the data into chunks and iterating over
        said chunks. The chunk size can be controlled via the incoming
        parameters.

        :param on_raw_data: Pandas DataFrame with raw data to be processed.
        :param num_rows_per_chunk: how many rows per chunk of data (if this
        value exceeds the number of total rows then there will be 1 chunk of
        data to process)

        :param do_randomize_chunks: should the chunks of data be
        selected at random?
        """
        # ensure the data has the correct columns
        with_format_code = str(with_format_code).strip()

        logger.info(f"Anchor data chunks in time?: {anchor_data_vs_time}.")

        if debug:
            logger.debug("Creating pipeline folder - results will go there...")
            pipeline_folder = kwargs.get('debug_folder', 'pipeline')

            if debug_folder_prepend is not None:
                pipeline_folder = "{}{}".format(debug_folder_prepend,
                                                pipeline_folder)
            if os.path.isdir(pipeline_folder):
                shutil.rmtree(pipeline_folder)

            os.mkdir(pipeline_folder)

            orig_dir = os.getcwd()
            logger.debug(f"Switching to folder '{pipeline_folder}'")
            os.chdir(pipeline_folder)

            columns_to_plot = list(set(on_raw_data.columns) - {'Date-Time'})
            plot_incoming_data = on_raw_data.loc[:, columns_to_plot]
            plot_incoming_data.plot()
            plt.savefig("incoming_raw_data.png")

        logger.debug("Subsample settings:")
        logger.debug(f"Number of subsamples = {number_of_subsamples}")
        logger.debug(f"Subsample size = {subsample_size_index}")

        # ability to pass around information between data chunks
        # was originally introduced due to the zero-line-filter
        parameters = dict()

        list_of_transformed_data_chunks = []
        for j, (this_chunk, sample_info) in enumerate(subsample_data(
                data=on_raw_data, number_of_subsamples=number_of_subsamples,
                subsample_size_index=subsample_size_index,
                use_subsampling=use_subsampling,
                randomize=randomize_subsampling,
                consecutive_subsamples=consecutive_subsamples,
                anchor_data_vs_time=anchor_data_vs_time,
                **kwargs)):

            # here we process the data in chunks generated by the iterator
            # "subsample_data". We do this for this main reason:
            # > some filters leverage detailed behavior of the data
            # (like values of the gradient) to make decisions. The more data
            # we expose at one time the more brittle the results get.
            #
            # Note that the option to pass around "parameters" between chunks
            # by it being updated by the filters means that in general we
            # cannot run the chunks in parallel
            chunk_ix = str(j + 1)
            msg = f"...Processing chunk {chunk_ix}; " \
                  f"chunk indices=({list(this_chunk.index)[0]}, " \
                  f"{list(this_chunk.index)[-1]})."
            logger.debug(msg)
            print(msg)
            if debug:
                # create data chunk directory
                chunk_dir_name = f"data_chunk {chunk_ix}"
                if not os.path.isdir(chunk_dir_name):
                    os.mkdir(chunk_dir_name)
                curr_dir = os.getcwd()
                os.chdir(chunk_dir_name)

            this_structured_data_chunk = self._run_chunk(
                on_raw_data_chunk=this_chunk,
                is_sorted=is_sorted, parameters=parameters,
                with_format_code=with_format_code,
                debug=debug)

            list_of_transformed_data_chunks.append(this_structured_data_chunk)

            if debug:
                os.chdir(curr_dir)

        # Note:
        # each chunk of data now has to be treated as an isolated segment
        # of data from the wearable for which a score needs to be computed.
        # Specifically, we should not concat all the chunks together since
        # there could generally be overlapping pieces (especially if using
        # the "random" subsampling method):
        # all_structured_data = pd.concat(all_structured_data_chunks)
        # all_structured_data.reset_index(drop=True, inplace=True)
        # also: if subsampling is False we just have a 1-element list now.

        logger.debug("Raw data successfully converted to structured data!")
        # always create structured data at the end of the pipeline:
        all_structured_data = DataFilterPipeline._create_structured_data(
            list_of_transformed_data_chunks=list_of_transformed_data_chunks,
            data_format_code=with_format_code)

        if debug:
            os.chdir(orig_dir)
            plt.close()

        return all_structured_data

    def _run_chunk(self, with_format_code='5',
                   on_raw_data_chunk=None, parameters=None, is_sorted=True, debug=False):
        """
        Runs the pipeline on incoming raw data.
        Returns structured data.

        :return:
        """
        # make sure the raw data points have unique indices:
        on_raw_data_chunk.reset_index(drop=True, inplace=True)

        # make sure to update the data format code:
        self.update_params(new_params=dict(data_format_code=with_format_code))

        initial_columns = list(on_raw_data_chunk.columns)

        initial_data = on_raw_data_chunk

        all_added_columns = []  # keep track of any additional/derivative data
        all_removed_columns = []

        current_data = on_raw_data_chunk.copy()
        for filter_ix, (filter_name, filter) in \
                enumerate(self._pipeline.items()):
            # now loop over, and apply, each filter to this chunk of data:

            if debug:
                # create filter directory inside this data chunk
                filter_dir_name = "filter-" + str(filter_ix + 1) + "-" + \
                                  filter_name
                if not os.path.isdir(filter_dir_name):
                    os.mkdir(filter_dir_name)
                curr_dir = os.getcwd()
                os.chdir(filter_dir_name)
                current_data.to_csv("data_in.csv", index=False)

                columns_to_plot = list(set(current_data.columns) -
                                       {'Date-Time'})
                data_in_plot = current_data.loc[:, columns_to_plot]
                data_in_plot.plot()
                plt.savefig("data_in.png")

                data_in_before_filter = deepcopy(current_data)


            if filter_name not in parameters:
                parameters[filter_name] = dict()

            self._results[filter] = dict()
            current_data, changes = filter.apply(data=current_data,
                                            parameters=parameters[filter_name]
                                                 )
            self._results[filter]['data'] = current_data
            self._results[filter]['changes'] = changes

            all_added_columns.append(changes.get('added', []))
            all_removed_columns.append(changes.get('removed', []))

            parameters[filter_name].update(**filter.get_parameters())

            if debug:
                current_data.to_csv("data_out.csv", index=False)

                with open("changes.json", "w") as fd:
                    json.dump(changes, fd)

                columns_to_plot = list(
                    set(current_data.columns) - {'Date-Time'})
                data_in_plot = current_data.loc[:, columns_to_plot]
                data_in_plot.plot()
                plt.savefig("data_out.png")

                # now only plot columns that have been affected:
                columns_to_plot = filter.columns_operated_on
                if columns_to_plot is not None and \
                        'Date-Time' not in columns_to_plot:
                    data_in_plot = current_data.loc[:, columns_to_plot]
                    data_in_plot.plot()
                    plt.savefig("data_out_only_affected_columns.png")

                # sometimes it can make sense to plot data before if columns
                # were there:
                try:
                    columns_to_plot = filter.columns_operated_on
                    if columns_to_plot is not None and \
                            'Date-Time' not in columns_to_plot:
                        data_in_plot = data_in_before_filter.loc[:, columns_to_plot]
                        data_in_plot.plot()
                        plt.savefig("data_in_only_affected_columns.png")
                except:
                    pass

                os.chdir(curr_dir)
                plt.close()

        all_added_columns = [item for sublist in all_added_columns for item in
                             sublist]
        all_removed_columns = [item for sublist in all_removed_columns for item
                               in sublist]

        assert len(all_removed_columns) == 0  # NEEDS implementation if >0

        assert current_data.shape[1] == len(list(
            np.unique(list(on_raw_data_chunk.columns) + all_added_columns)))

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

        # TODO(JTK): these should be filters too (sorting etc.)
        if not is_sorted:
            data_post_pipeline.sort_values(by=['Date-Time'], ascending=True,
                                           inplace=True)
        data_post_pipeline.drop_duplicates(subset=['Date-Time'], inplace=True)

        logger.debug("After dropping duplicates we have "
                     "{} pts.".format(len(data_post_pipeline)))

        if debug:
            plt.close()

        return current_data

    def describe(self):
        """List this pipeline with its filters."""
        structure = dict()  # pipeline structure
        for filter_ix, (filter_name, filter) in \
                enumerate(self._pipeline.items()):

            key = str(filter)[1:].split(' object at ')[0]
            structure[key] = filter.get_parameters()
            structure[key]['user_defined_name'] = filter_name
            structure[key]['position'] = filter_ix  # position in the pipeline

        return structure

    @staticmethod
    def _create_structured_data(list_of_transformed_data_chunks=None,
                                data_format_code='5'):
        """
        Taking in a list of transformed data chunks (i.e., each element in
        the list is a transformed data element - it has gone through
        the ETL pipeline) this method returns a list of same length where
        the ith element is now the structured data version of the transformed
        raw data.
        """

        all_chunks_of_structured_data = []
        for data_chunk_transformed in list_of_transformed_data_chunks:
            f_str_data = CreateStructuredData()
            f_str_data.update(new_params=dict(
                data_format_code=data_format_code))
            structured_data, _ = f_str_data.apply(data=data_chunk_transformed)
            all_chunks_of_structured_data.append(structured_data)

        return all_chunks_of_structured_data

    def get_result(self, name=None):
        """
        Returns the results of a filter.
        """
        return self._results[name]

    def get_parameters(self, name=None):
        """
        Returns the parameters of a filter.
        """
        return self._pipeline[name].get_parameters()
