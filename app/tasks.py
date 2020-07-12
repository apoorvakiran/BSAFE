# -*- coding: utf-8 -*-
"""This is a simple system (end-to-end) going from raw data all the way
through reporting.

@ author James Russo, Jesper Kristensen
Copyright Iterate Labs Inc. 2018-
All Rights Reserved.
"""

__author__ = "James Russo, Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import logging
import os
import datetime
from numpy import ceil
from urllib.error import HTTPError
from periodiq import cron
from app.api_client import ApiClient
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
from ergo_analytics.metrics import AngularActivityScore
from ergo_analytics.metrics import PostureScore

from .extensions import dramatiq

logger = logging.getLogger()
api_client = ApiClient()


def run_BSAFE(raw_data=None, mac_address=None, run_as_test=False, **kwargs):
    """Given raw data run BSAFE on the data.

    Run BSAFE on incoming raw_data.
    """

    if raw_data is None:
        logger.info(f"Found no elements in the ES database for {mac_address}.")
        return

    logger.info(
        f"Found {len(raw_data)} elements in " f"the ES database for {mac_address}."
    )
    logger.info(raw_data.head(10))

    num_data = len(raw_data)
    # take 10% as subsampling but not below 1 minute:
    subsample_size_index = ceil(max(num_data * 0.1, 600))
    logger.debug(f"Using {subsample_size_index} indices per subsample!")

    # now pass the raw data through our data filter pipeline:
    pipeline = DataFilterPipeline()
    # instantiate the filters:
    pipeline.add_filter(name="fix_osc", filter=FixDateOscillations())
    # pipeline.add_filter(name='centering1', filter=DataCentering())
    pipeline.add_filter(name="delta_values", filter=ConstructDeltaValues())
    pipeline.add_filter(name="centering2", filter=DataCentering())
    pipeline.add_filter(name="window", filter=WindowOfRelevantDataFilter())
    pipeline.add_filter(name="impute", filter=DataImputationFilter())
    pipeline.add_filter(name="quadrant_fix", filter=QuadrantFilter())
    # run the pipeline!

    if run_as_test:
        raw_data.to_csv("log.csv", index=False)

    list_of_structured_data_chunks = pipeline.run(on_raw_data=raw_data, **kwargs,)

    em = None
    logger.info(f"Retrieved all data for {mac_address}")
    if len(list_of_structured_data_chunks) > 0:
        logger.info(f"Has data to run analysis on for {mac_address}")
        em = ErgoMetrics(list_of_structured_data_chunks=list_of_structured_data_chunks)
        # add metrics to compute:
        metrics = {"activity": AngularActivityScore, "posture": PostureScore}
        for m_name in metrics:
            em.add(metric=metrics[m_name])
        em.compute()
        logger.info(f"Metrics generated for {mac_address}")
        # the report is set up in the context of a device and its
        # corresponding ergoMetrics data:

        report = ErgoReport(ergo_metrics=em)
        # now we can report to any format we want - here HTTP:

        report.to_http(
            api_client=api_client,
            mac_address=mac_address,
            run_as_test=run_as_test,
            **kwargs,
        )
        logger.info(report.response)
        logger.info(f"{report.response.status_code} " f"{report.response.text}")
        logger.info(f"Created safety_score for {mac_address}")

        logger.info("JSON = {}".format(report.to_json()))
    else:
        logger.info(f"No values to analyze for {mac_address}")

    if run_as_test:
        if em is not None:
            return em.get_score("safety_score")


@dramatiq.actor(periodic=cron("*/15 * * * *"))
def automated_analysis():
    logger.info("Running automated analysis")
    current_time = datetime.datetime.utcnow()
    end_time = datetime.datetime.utcnow().isoformat()
    start_time = (current_time - datetime.timedelta(minutes=15)).isoformat()
    try:
        response = api_client.get_request("api/v1/wearables?automated=true")
        response.raise_for_status()
        wearables = response.json()["data"]
        logger.info(f"Running automated analysis for {len(wearables)}")
        for wearable in wearables:
            mac_address = wearable["attributes"]["mac"]
            logger.info(f"Running analysis for {mac_address}")
            safety_score_analysis.send(mac_address, start_time, end_time)
        logger.info(f"Enqueued all analysis")
    except HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}", exc_info=True)
    except Exception as err:
        logger.error(f"Failure to send request {err}", exc_info=True)


@dramatiq.actor(max_retries=3)
def safety_score_analysis(mac_address, start_time, end_time, run_as_test=False):
    logger.info(f"Getting safety score for {mac_address}")
    index = os.getenv("ELASTIC_SEARCH_INDEX", "iterate-labs-local-poc")
    host = os.getenv("ELASTIC_SEARCH_HOST")

    data_format_code = "5"  # what format is the data in?

    # subsampling of the data:
    how_to_combine_across_parameter = "average"  # note: cannot be "keep separate"
    number_of_subsamples = 10
    randomize_subsampling = False
    use_subsampling = False

    data_loader = LoadElasticSearch()
    raw_data = data_loader.retrieve_data(
        mac_address=mac_address,
        start_time=start_time,
        end_time=end_time,
        host=host,
        index=index,
        data_format_code=data_format_code,
        limit=None,
    )

    options = {
        "with_format_code": data_format_code,
        "use_subsampling": use_subsampling,
        "randomize_subsampling": randomize_subsampling,
        "number_of_subsamples": number_of_subsamples,
        "combine_across_parameter": how_to_combine_across_parameter,
    }
    run_BSAFE(
        raw_data=raw_data, mac_address=mac_address, run_as_test=run_as_test, **options
    )


@dramatiq.actor(max_retries=3)
def status():
    """Health check: Check that the BSAFE code is functioning properly.

    Used in K8S health check.

    Returns:
        200 (int) if BSAFE works as expected.
        500 (int) if there are issues with BSAFE or the Elastic Search Database.
    """
    data_format_code = "5"  # determined automatically in the data loader if incorrect

    data_loader = LoadElasticSearch()
    mac_address, raw_data = data_loader.retrieve_any_macaddress_with_data()

    if raw_data is None:
        logger.warning(
            f"/STATUS: Found no elements in the ES database for '{mac_address}' during status check."
        )
        return 500

    # subsampling of the data:
    how_to_combine_across_parameter = "average"  # note: cannot be "keep separate"
    number_of_subsamples = 10
    randomize_subsampling = False
    use_subsampling = False

    options = {
        "with_format_code": data_format_code,
        "use_subsampling": use_subsampling,
        "randomize_subsampling": randomize_subsampling,
        "number_of_subsamples": number_of_subsamples,
        "combine_across_parameter": how_to_combine_across_parameter,
    }
    score = run_BSAFE(
        raw_data=raw_data, mac_address=mac_address, run_as_test=True, **options
    )

    if score is None:
        logger.warning("Score could not be computed by BSAFE!")

    return 200 if score is not None else 500
