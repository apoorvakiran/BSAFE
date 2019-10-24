# -*- coding: utf-8 -*-
"""

@ author Jesper Kristensen
Copyright 2018-
"""

__all__ = ["DataImputationFilter"]
__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

from . import BaseTransformation
import logging

logger = logging.getLogger()


class DataImputationFilter(BaseTransformation):

    def __init__(self, columns=None):
        super().__init__(columns=columns)

    def _initialize_params(self):
        self._params = dict(method='nan')

    def apply(self, data=None):
        """
        Imputes the data or rids of it depending on the method used.

        :param data:
        :return:
        """
        super().apply(data=data)

        # right now the data imputation is easy: Just get rid
        # of the NaN values - but going forward we can have more
        # complex methods such as sampling from statistical distributions:
        # For example: Create a multi-variate Gaussian on all data we do have
        # and then sample from it conditioned on the data we _do_ have at other
        # rows to find likely values for the missing data.
        if self._params['method'] == 'nan':
            logger.info("# of data before filtering for NaNs... = "
                        "{}".format(len(data)))

            if self._columns == 'all':
                self._columns = data.columns

            data.dropna(how='any', inplace=True, subset=self._columns, axis=0)
            logger.info("# of data after filtering away NaNs... = "
                        "{}".format(len(data)))
        else:
            raise NotImplementedError("Implement me!")

        return self._update_data(data_transformed=data), {}
