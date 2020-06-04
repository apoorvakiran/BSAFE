# -*- coding: utf-8 -*-
"""Compute metrics for analyzing a collection of structured data.

Stores a list of metric objects (defined under "metrics" folder) and
just calls their compute method.

@ author Jesper Kristensen
Copyright Iterate Labs, Inc. 2018
"""

__all__ = ["ErgoMetrics"]
__author__ = "Iterate Labs, Inc."
__version__ = "Alpha"

import numpy as np
import pandas as pd
import logging
from .data_structured import StructuredData

logger = logging.getLogger()


class ErgoMetrics(object):
    """Computes Ergonomic Metrics (ErgoMetrics) for the incoming data
    which is assumed to be in "structured" form as opposed to "raw" data.

    The Ergo Metrics is what is responsible for creating the ergonomics
    scores and provide an evaluation for management and people in
    charge of the safety.
    """

    _data_chunks = None
    _number_of_data_chunks = None
    _scores = None
    _metrics_to_use = None

    def __init__(self, list_of_structured_data_chunks=None):
        """Constructs an object from which metrics can be computed
        based off of "Structured Data".

        :param structured_data:
        :param data_id: If run from data in the data store this is provided.
        """

        if list_of_structured_data_chunks is None:
            msg = "Please pass in list of valid data chunks!"
            logger.exception(msg)
            raise Exception(msg)

        self._data_chunks = list_of_structured_data_chunks

        self._number_of_data_chunks = len(self._data_chunks)
        self._scores = dict()
        self._metrics_to_use = dict()

    @property
    def metrics(self):
        """Which metrics do we have."""
        return list(self._metrics_to_use.keys())

    def add(self, metric=None, name=None):
        """Adds a metric to this object to be computed."""
        self._metrics_to_use[name] = metric

    def remove(self, name=None):
        """Removes a metric via its given name from
        the internal list of metrics"""
        if name in self._metrics_to_use:
            del [self._metrics_to_use[name]]
        else:
            raise ValueError(f"Invalid metric; options " f"are: {list(self._metrics_to_use.keys())}")

    @property
    def earliest_time(self):
        """Earliest time for which we have data."""

        earliest_time = None
        for data_chunk in self._data_chunks:
            if not isinstance(data_chunk, StructuredData):
                continue

            this_min_time = data_chunk.time.min()

            if earliest_time is None:
                earliest_time = this_min_time
                continue

            earliest_time = min(earliest_time, this_min_time)

        return earliest_time

    @property
    def latest_time(self):
        """Latest time for which we have data."""

        latest_time = None
        for data_chunk in self._data_chunks:
            if not isinstance(data_chunk, StructuredData):
                continue

            this_max_time = data_chunk.time.max()

            if latest_time is None:
                latest_time = this_max_time
                continue

            latest_time = max(latest_time, this_max_time)

        return latest_time

    def _delta_yaw(self, chunk_index=0):
        try:
            data = self._data_chunks[chunk_index].get_data(type="yaw", loc="delta")
        except AttributeError:
            return None
        return data

    def _delta_pitch(self, chunk_index=0):
        try:
            data = self._data_chunks[chunk_index].get_data(type="pitch", loc="delta")
        except AttributeError:
            return None

        return data

    def _delta_roll(self, chunk_index=0):
        try:
            data = self._data_chunks[chunk_index].get_data(type="roll", loc="delta")
        except AttributeError:
            return None
        return data

    @property
    def data(self, chunk_index=None):
        """Return the data used by this ErgoMetrics object."""
        if chunk_index is None:
            return self._data_chunks
        else:
            return self._data_chunks[chunk_index]

    def get_first_data_index(self, chunk_index=None):
        """Return the first index of the data for this chunk index."""
        if chunk_index is not None:
            if isinstance(self._data_chunks[chunk_index], StructuredData):
                return self._data_chunks[chunk_index].get_first_index()

    def get_last_data_index(self, chunk_index=None):
        """Return the last index of the data for this chunk index."""
        if chunk_index is not None:
            if isinstance(self._data_chunks[chunk_index], StructuredData):
                return self._data_chunks[chunk_index].get_last_index()

    @property
    def number_of_data_chunks(self):
        return self._number_of_data_chunks

    def compute(self, debug=False, store_plots_here=None, metrics_parameters=None, **kwargs):
        """Compute the ergo metric scores called "ergoMetrics" or "ergoScores".

        For each metric added to this object, the score value of that metric is
        computed and stored in an internal dictionary.

        :param debug: Whether to turn on plotting and more details.
        """
        # compute the scores
        logger.debug("Computing ErgoMetric scores...")

        if metrics_parameters is None:
            metrics_parameters = dict()

        # compute a score for each chunk of data:
        num_good_chunks = 0
        for chunk_index in range(self._number_of_data_chunks):

            self._scores[chunk_index] = dict()

            if self._data_chunks[chunk_index] is None or isinstance(self._data_chunks[chunk_index], list):
                if self._data_chunks[chunk_index] is not None:
                    assert len(self._data_chunks[chunk_index]) == 0
                continue

            # compute each metric:
            for metric_name in self._metrics_to_use:

                these_params = metrics_parameters.get(metric_name, dict())

                metric = self._metrics_to_use[metric_name]
                metric = metric()
                this_score = metric.compute(
                    delta_pitch=self._delta_pitch(chunk_index=chunk_index),
                    delta_yaw=self._delta_yaw(chunk_index=chunk_index),
                    delta_roll=self._delta_roll(chunk_index=chunk_index),
                    method="rolling_window",
                    debug=debug,
                    prepend=chunk_index,
                    store_plots_here=store_plots_here,
                    **these_params,
                    **kwargs,
                )

                self._scores[chunk_index][metric_name] = dict()
                self._scores[chunk_index][metric_name]["score"] = this_score
                # self._scores[chunk_index][metric_name]['params_used'] = params_used
                self._scores[chunk_index][metric_name]["index"] = chunk_index
                self._scores[chunk_index][metric_name]["data_index_from"] = self._data_chunks[
                    chunk_index
                ].get_first_index()
                self._scores[chunk_index][metric_name]["data_index_till"] = self._data_chunks[
                    chunk_index
                ].get_last_index()

                this_data_chunk = self._data_chunks[chunk_index]

                if this_data_chunk is not None and isinstance(this_data_chunk, StructuredData):
                    data_index_from = this_data_chunk.get_first_index()
                    data_index_till = this_data_chunk.get_last_index()
                else:
                    data_index_from = None
                    data_index_till = None

                self._scores[chunk_index][metric_name]["data_index_from"] = data_index_from
                self._scores[chunk_index][metric_name]["data_index_till"] = data_index_till

            num_good_chunks += 1

        if num_good_chunks == 0:
            msg = "No good data chunks found!"
            logger.debug(msg)

        logger.debug("Done!")

    def get_score(self, name=None, combine_across_parameter="median", chunk_index=0, **kwargs):
        """Returns the score of metric with name "name".

        Combine can be one of {"average", "max", None}
        (if None: go by chunk_index and thus return score for single chunk).
        If combine is not None, then that is favored over a single score
        from a single chunk.
        """

        if name is None:
            options = list(self._metrics_to_use.keys())
            if len(options) == 0:
                raise Exception("Please run the ErgoMetrics with metrics first!")
            raise ValueError(f"Name is invalid; options " f"are: {options}")

        if len(self._scores) == 0:
            msg = "Please compute the Ergo Metrics scores first!\n" "Do this by calling the .compute() method."
            logger.exception(msg)
            raise Exception(msg)

        all_scores = []
        for chunk_index in self._scores:
            this_score = self._get_score_single_chunk(name=name, chunk_index=chunk_index)
            all_scores.append(this_score)

        if callable(combine_across_parameter):
            combiner = combine_across_parameter
        elif combine_across_parameter == "average":
            combiner = np.average
        elif combine_across_parameter == "median":
            combiner = np.median
        elif combine_across_parameter == "max":
            combiner = np.max
        elif combine_across_parameter == "keep-separate":

            def keep_separate(x=None, axis=0):
                """Do not combine scores for this single data chunk
                in any way - keep them separate."""
                # return incoming scores as:
                # [[yaw_1, pitch_1, roll_1], ..., [yaw_N, pitch_N, roll_N]]
                # where the index is over any parameter that was used
                # to create the score
                # (such as "angle threshold" in the "strain score")
                return np.hstack(x.values)

            combiner = keep_separate
        else:
            msg = f"The combine_across_parameter method '{combine_across_parameter}' is not supported!"
            logger.exception(msg)
            raise Exception(msg)

        final_score = []
        for el in all_scores:
            # here we loop over the scores for each chunk of data.
            # Generally, the score for a _single_ chunk can be in the form:
            # [[yaw1, pitch1, roll1],
            #  [yaw2, pitch2, roll2],
            #  [yaw3, pitch3, roll3]]
            # where the indices identify the parameter.
            # The reason is that a parameter can be used to compute
            # the scores with (such as "30", "40", "50" as angle
            # threshold for posture score).

            # So note: We are not combining over the chunks themselves
            if el is None or el.empty:
                this_combined_score = [None, None, None]
            else:
                this_combined_score = combiner(el, axis=1).tolist()

            final_score.append(this_combined_score)

        return final_score

    def _get_score_single_chunk(self, name=None, chunk_index=0):
        """Returns the score "name" for a single data "chunk_index"."""

        if len(self._scores[chunk_index]) == 0:
            # no data for this chunk:
            if self._data_chunks[chunk_index] is not None:
                assert len(self._data_chunks[chunk_index]) == 0
            return

        scores = self._scores[chunk_index][name]["score"]  # {p0: ..., p1: ...}
        scores = pd.DataFrame.from_dict(scores)

        return scores
