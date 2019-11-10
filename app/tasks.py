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
import datetime
import requests
from periodiq import PeriodiqMiddleware, cron
from ergo_analytics import LoadElasticSearch
from ergo_analytics import DataFilterPipeline
from ergo_analytics.filters import FixDateOscillations
from ergo_analytics.filters import DataCentering
from ergo_analytics.filters import ConstructDeltaValues
from ergo_analytics.filters import WindowOfRelevantDataFilter
from ergo_analytics.filters import DataImputationFilter
from ergo_analytics.filters import QuadrantFilter
from ergo_analytics import ErgoMetrics
from ergo_analytics import ErgoReport
from constants import DATA_FORMAT_CODES

from .extensions import dramatiq

logger = logging.getLogger()

@dramatiq.actor(periodic=cron('*/15 * * * *'))
def automated_analysis():
    logger.info("Running automated analysis")
    current_time = datetime.datetime.utcnow()
    end_time = datetime.datetime.utcnow().isoformat()
    start_time = (current_time - datetime.timedelta(minutes=15)).isoformat()
    headers = {'Authorization': f"Bearer {os.getenv('INFINITY_GAUNTLET_AUTH')}"}
    try:
        response = requests.get(
            f"{os.getenv('INFINITY_GAUNTLET_URL')}/api/v1/wearables?automated=true",
            headers=headers
        )
        response.raise_for_status()
        wearables = response.json()['data']
        logger.info(f"Running automated analysis for {len(wearables)}")
        for wearable in wearables:
            mac_address = wearable['attributes']['mac']
            logger.info(f"Running analysis for {mac_address}")
            safety_score_analysis.send(mac_address, start_time, end_time)
        logger.info(f"Enqueued all analysis")
    except HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}", exc_info=True)
    except Exception as err:
        logger.error(f"Failure to send request {err}", exc_info=True)


@dramatiq.actor(max_retries=3)
def safety_score_analysis(mac_address, start_time, end_time):
    logger.info(f"Getting safety score for {mac_address}")
    index = os.getenv('ELASTIC_SEARCH_INDEX', 'iterate-labs-local-poc')
    host = os.getenv('ELASTIC_SEARCH_HOST')

    data_format_code = '5'  # what format is the data in?

    data_loader = LoadElasticSearch()
    raw_data = data_loader.retrieve_data(mac_address=mac_address,
                                         start_time=start_time,
                                         end_time=end_time,
                                         host=host, index=index,
                                         data_format_code=data_format_code)
    if raw_data is None:
        logger.info(f"Found no elements in the ES database for {mac_address}.")
        return
    logger.info(f"Found {len(raw_data)} elements in "
                f"the ES database for {mac_address}.")

    # now pass the raw data through our data filter pipeline:
    pipeline = DataFilterPipeline()
    # instantiate the filters:
    pipeline.add_filter(name='fix_osc', filter=FixDateOscillations())
    pipeline.add_filter(name='centering1', filter=DataCentering())
    pipeline.add_filter(name='delta_values', filter=ConstructDeltaValues())
    pipeline.add_filter(name='centering2', filter=DataCentering())
    pipeline.add_filter(name='window', filter=WindowOfRelevantDataFilter())
    pipeline.add_filter(name='impute', filter=DataImputationFilter())
    pipeline.add_filter(name='quadrant_fix', filter=QuadrantFilter())
    # run the pipeline!
    structured_data = pipeline.run(on_raw_data=raw_data,
                                   with_format_code=data_format_code)

    logger.info(f"Retrieved all data for {mac_address}")
    if structured_data.number_of_points > 0:
        logger.info(f"Has data to run analysis on for {mac_address}")
        metrics = ErgoMetrics(structured_data=structured_data)
        metrics.compute()
        logger.info(f"Metrics generated for {mac_address}")
        # the report is set up in the context of a device and its
        # corresponding ergoMetrics data:
        report = ErgoReport(ergo_metrics=metrics, mac_address=mac_address)
        # now we can report to any format we want - here HTTP:
        auth = f"Bearer {os.getenv('INFINITY_GAUNTLET_AUTH')}"
        report.to_http(endpoint=f"{os.getenv('INFINITY_GAUNTLET_URL')}/api/v1/"
                                f"safety_scores",
                       authorization=auth)

        logger.info(f"{report.response.status_code} "
                    f"{report.response.text}")
        logger.info(f"Created safety_score for {mac_address}")
    else:
        logger.info(f"No values to analyze for {mac_address}")
