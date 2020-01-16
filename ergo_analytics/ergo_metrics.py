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
            del[self._metrics_to_use[name]]
        else:
            raise ValueError(f"Invalid metric; options "
                             f"are: {list(self._metrics_to_use.keys())}")

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
            data = self._data_chunks[chunk_index].get_data(
                type='yaw', loc='delta')
        except AttributeError:
            return None
        return data

    def _delta_pitch(self, chunk_index=0):
        try:
            data = self._data_chunks[chunk_index].get_data(type='pitch',
                                                           loc='delta')
        except AttributeError:
            return None

        return data

    def _delta_roll(self, chunk_index=0):
        try:
            data = self._data_chunks[chunk_index].get_data(type='roll',
                                                           loc='delta')
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

    def compute(self, debug=False, store_plots_here=None, **kwargs):
        """Compute the ergo metric scores called "ergoMetrics" or "ergoScores".

        For each metric added to this object, the score value of that metric is
        computed and stored in an internal dictionary.

        :param debug: Whether to turn on plotting and more details.
        """
        # compute the scores
        logger.debug("Computing ErgoMetric scores...")

        # compute a score for each chunk of data:
        num_good_chunks = 0
        for chunk_index in range(self._number_of_data_chunks):

            self._scores[chunk_index] = dict()

            # compute each metric
            for metric_name in self._metrics_to_use:

                metric = self._metrics_to_use[metric_name]
                metric = metric()
                this_score = metric.compute(delta_pitch=self._delta_pitch(chunk_index=chunk_index),
                                            delta_yaw=self._delta_yaw(chunk_index=chunk_index),
                                            delta_roll=self._delta_roll(chunk_index=chunk_index),
                                            method='rolling_window', debug=debug, prepend=chunk_index,
                                            store_plots_here=store_plots_here, **kwargs)

                self._scores[chunk_index][metric_name] = this_score

            num_good_chunks += 1

        if num_good_chunks == 0:
            msg = "No good data chunks found!"
            logger.debug(msg)

        logger.debug("Done!")

    def get_score(self, name=None, combine='median', chunk_index=0):
        """
        Returns the score of metric with name "name".

        Combine can be one of {"average", "max", None}
        (if None: go by chunk_index and thus return score for single chunk).
        If combine is not None, then that is favored over a single score
        from a single chunk.
        """

        if name is None:
            raise ValueError(f"Name is invalid; options "
                             f"are: {list(self._metrics_to_use.keys())}")

        if len(self._scores) == 0:
            msg = "Please compute the Ergo Metrics scores first!\n"\
                  "Do this by calling the .compute() method."
            logger.exception(msg)
            raise Exception(msg)

        if combine is None:
            # just return single score as per incoming chunk index:
            if chunk_index is None:
                msg = "Please pass in a valid chunk index (such as 0)!"
                logger.exception(msg)
                raise Exception(msg)

            final_score = self._get_score_single_chunk(name=name,
                                                       chunk_index=chunk_index)
        else:
            # the user wants a combination of all the scores from the various
            # data chunks:
            all_scores = []
            for chunk_index in self._scores:
                this_score = self._get_score_single_chunk(name=name,
                                                        chunk_index=chunk_index)
                all_scores.append(this_score)

            if callable(combine):
                final_score = combine(all_scores)
            elif combine == 'average':
                final_score = np.average(all_scores)
            elif combine == 'median':
                final_score = np.median(all_scores)
            elif combine == 'max':
                final_score = np.max(all_scores)
            else:
                msg = f"The combine method '{combine}' is not supported!"
                logger.exception(msg)
                raise Exception(msg)

        return final_score

    def _get_score_single_chunk(self, name=None, chunk_index=0):
        """Returns the score "name" for a single data "chunk_index".
        """
        scores = self._scores[chunk_index].copy()

        name = name.split('/')  # support naming like "speed/yaw", etc.
        for n in name:
            if n not in scores:
                msg = f"Was unable to find the score with name '{n}'.\n"
                msg += f"Possible score names are: {list(scores.keys())}."
                logger.exception(msg)
                raise Exception(msg)

            scores = scores[n]

        return scores
