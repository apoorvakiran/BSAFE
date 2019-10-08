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

from . import WindowOfRelevantDataFilter
from . import QuadrantFilter
from . import ConstructDeltaValues
from . import CreateStructuredData
from . import FixDateOscillations
from . import DataImputationFilter
from . import DataCentering
from constants import DATA_FORMAT_CODES
import logging

logger = logging.getLogger()


class DataFilterPipeline(object):
    """
    Pipeline of tasks capabile of taking in a raw data object, applying
    transformations, and outputting a structured data object.

    The pipeline leverages the filters in "Data_Filters".
    """

    _data_format_code = None

    def __init__(self, data_format_code='4'):
        """
        Constructs an object from which metrics can be computed
        based off of a "Structured Data" object.

        :param raw_data: the raw data to process
        :param is_streaming: is the data coming in, in a streaming format?
        """

        self._data_format_code = data_format_code

    def run(self, raw_data=None):
        """
        Runs the pipeline on incoming raw data.
        Returns structured data.

        :return:
        """

        initial_data = raw_data

        # first - which columns to apply the filter to?
        # TODO(Jesper): We could imagine saying
        #  "these columns for this filter" and so on...
        numeric_columns = DATA_FORMAT_CODES[self._data_format_code]['NUMERICS']

        # ===== PIPELINE START
        # correct date oscillations:
        t_date_oscillations = FixDateOscillations(columns='all')
        data_transformed = t_date_oscillations.apply(data=raw_data)

        # center the data:
        if self._data_format_code == '4':
            t_dc = DataCentering(columns=['DeltaYaw', 'DeltaPitch',
                                          'DeltaRoll'])
            data_transformed = t_dc.apply(data=data_transformed)
        else:
            raise NotImplementedError("Implement me!")

        # now construct delta values if needed:
        t_delta_filter = ConstructDeltaValues(columns=numeric_columns)
        data_transformed, delta_columns = t_delta_filter.apply(
            data=data_transformed,
            data_format_code=self._data_format_code)

        # now center the delta values:
        # TODO(Jesper) GENERALLY here we want to center the delta values
        # upon their construction (for data format 4 we don't need to)

        # now find the region of relevant data:
        t_window_filter = WindowOfRelevantDataFilter(columns=delta_columns)
        data_transformed = t_window_filter.apply(data=data_transformed)

        t_impute = DataImputationFilter(columns='all')
        data_transformed = t_impute.apply(data=data_transformed, method='nan')

        quad = QuadrantFilter(columns=numeric_columns)
        data_transformed = quad.apply(data=data_transformed)
        # ===== PIPELINE END

        # now what data remains?
        data_post_pipeline = initial_data.iloc[data_transformed.index, :]
        data_post_pipeline.loc[:, data_transformed.columns] = \
            data_transformed

        # sort, drop duplicates, and reset index:
        logger.debug("Dropping duplicate data "
                     "points - currently we have "
                     "{} pts.".format(len(data_post_pipeline)))

        data_post_pipeline.sort_values(by=['Date-Time'], ascending=True,
                                       inplace=True)
        data_post_pipeline.drop_duplicates(subset=['Date-Time'], inplace=True)
        data_post_pipeline.reset_index(drop=True, inplace=True)

        logger.debug("After dropping duplicates we have "
                     "{} pts.".format(len(data_post_pipeline)))

        t_str_data = CreateStructuredData(columns='all')
        structured_data = t_str_data.apply(data=data_post_pipeline,
                                        data_format_code=self._data_format_code)

        logger.debug("Raw data successfully converted to structured data!")

        if len(structured_data) == 1:
            logger.warning("You only have 1 data point to analyze!")

        return structured_data
