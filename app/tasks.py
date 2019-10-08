# -*- coding: utf-8 -*-
"""
This is a simple system (end-to-end) going from raw data all the way
through reporting.

This code also serves as a "get started" for newcomers to BSAFE.

@ author James Russo, Jesper Kristensen, Jacob Tyrrell
Copyright Iterate Labs Inc. 2018-
"""

__author__ = "James Russo, Jesper Kristensen, Jacob Tyrrell"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import logging
import os
from periodiq import PeriodiqMiddleware, cron
from ergo_analytics import ErgoMetrics
from ergo_analytics import LoadElasticSearch
from ergo_analytics import DataFilterPipeline
from ergo_analytics import ErgoReport

from .extensions import dramatiq

logger = logging.getLogger()

@dramatiq.actor(periodic=cron('* * * * *'))
def heartbeat():
    logger.info("Pulse")

@dramatiq.actor
def safety_score_analysis(mac_address, from_date, till_date):
    logger.info(f"Getting safety score for {mac_address}")
    index = os.getenv('ELASTIC_SEARCH_INDEX', 'iterate-labs-local-poc')
    host = os.getenv('ELASTIC_SEARCH_HOST')

    data_loader = LoadElasticSearch()
    raw_data = data_loader.retrieve_data(mac_address=mac_address,
                                         from_date=from_date,
                                         till_date=till_date,
                                         host=host, index=index,
                                         data_format_code=4)

    logger.info("Found {} elements in the ES database.".format(len(raw_data)))

    transformer = DataFilterPipeline(data_format_code='4')
    structured_data = transformer.run(raw_data=raw_data)

    logger.info(f"Retrieved all data for {mac_address}")
    if structured_data.number_of_points > 0:
        logger.info(f"Has data to run analysis on for {mac_address}")
        metrics = ErgoMetrics(structured_data=structured_data)
        logger.info(f"Metrics generated for {mac_address}")
        report = ErgoReport(
            'http',
            metrics,
            f"Bearer {os.getenv('INFINITY_GAUNTLET_AUTH')}",
            f"{os.getenv('INFINITY_GAUNTLET_URL')}/api/v1/safety_scores",
            mac_address
        )
        logger.info(f"{report._sent.status_code} {report._sent.text}")
        logger.info(f"Created safety_score for {mac_address}")
    else:
        logger.info(f"No values to analyze for {mac_address}")
