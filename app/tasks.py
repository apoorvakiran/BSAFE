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
from ergo_analytics import ErgoMetrics
from ergo_analytics import ErgoReport
from ergo_analytics.setup_utilities import (
    parse_bsafe_yaml,
    construct_datafilter_pipeline,
    construct_metrics,
)
from .extensions import dramatiq

logger = logging.getLogger()
api_client = ApiClient()


def run_BSAFE(
    raw_data=None,
    mac_address=None,
    run_as_test=False,
    with_format_code=None,
    scoring_definition=None,
    scoring_hash=None,
    bsafe_setup_filename=None,
):
    """Given raw data run BSAFE on the data."""

    if raw_data is None:
        logger.info(f"Found no elements in the ES database for {mac_address}.")
        return

    logger.info(
        f"Found {len(raw_data)} elements in " f"the ES database for {mac_address}."
    )
    logger.info(raw_data.head(10))  # show some elements from the data found

    if scoring_definition is None:
        if bsafe_setup_filename is None:
            raise ValueError("Please provide a valid BSAFE setup YAML file!")

        scoring_definition, scoring_hash = parse_bsafe_setup_file(
            bsafe_setup_filename=bsafe_setup_filename
        )

    if scoring_definition is None:
        scoring_definition = dict()

    # Construct Data Filter Pipeline from the YAML definition file:
    pipeline = construct_datafilter_pipeline(scoring_definition=scoring_definition)
    # Construct metrics as specified in the YAML definition file:
    metrics, metrics_parameters = construct_metrics(
        scoring_definition=scoring_definition
    )

    num_data = len(raw_data)
    # take 10% as subsampling but not below 1 minute:
    subsample_size_index = ceil(max(num_data * 0.1, 600))
    logger.info(f"Using {subsample_size_index} indices per subsample!")

    if run_as_test:
        raw_data.to_csv("log.csv", index=False)

    if raw_data is None:
        raw_data = scoring_definition.get("on_raw_data", None)

    if raw_data is None:
        raise ValueError("Raw data is None!")

    if with_format_code is None:
        with_format_code = scoring_definition.get("with_format_code", None)

    is_sorted = scoring_definition.get("is_sorted", True)
    use_subsampling = scoring_definition.get("use_subsampling", False)
    number_of_subsamples = scoring_definition.get("number_of_subsamples", 10)
    randomize_subsampling = scoring_definition.get("randomize_subsampling", False)
    consecutive_subsamples = scoring_definition.get("consecutive_subsamples", False)
    subsample_size_index = scoring_definition.get("subsample_size_index", 1000)
    debug = scoring_definition.get("debug", False)
    debug_folder_prepend = scoring_definition.get("debug_folder_prepend", None)
    anchor_data_vs_time = scoring_definition.get("anchor_data_vs_time", False)

    _delete_keys(
        [
            "is_sorted",
            "use_subsampling",
            "number_of_subsamples",
            "randomize_subsampling",
            "consecutive_subsamples",
            "subsample_size_index",
            "debug",
            "debug_folder_prepend",
            "anchor_data_vs_time",
            "with_format_code",
        ],
        scoring_definition,
    )

    list_of_structured_data_chunks = pipeline.run(
        on_raw_data=raw_data,
        with_format_code=with_format_code,
        is_sorted=is_sorted,
        use_subsampling=use_subsampling,
        number_of_subsamples=number_of_subsamples,
        randomize_subsampling=randomize_subsampling,
        consecutive_subsamples=consecutive_subsamples,
        subsample_size_index=subsample_size_index,
        debug=debug,
        debug_folder_prepend=debug_folder_prepend,
        anchor_data_vs_time=anchor_data_vs_time,
        **scoring_definition,
    )

    em = None
    logger.info(f"Retrieved all data for {mac_address}")
    if len(list_of_structured_data_chunks) > 0:
        logger.info(f"Has data to run analysis on for {mac_address}")
        em = ErgoMetrics(list_of_structured_data_chunks=list_of_structured_data_chunks)
        # add metrics to compute:
        for m_name in metrics:
            em.add(metric=metrics[m_name])

        em.compute(metrics_parameters=metrics_parameters, **scoring_definition)

        logger.info(f"Metrics generated for {mac_address}")
        # the report is set up in the context of a device and its
        # corresponding ergoMetrics data:

        report = ErgoReport(ergo_metrics=em)
        # now we can report to any format we want - here HTTP:

        report.to_http(
            api_client=api_client,
            mac_address=mac_address,
            run_as_test=run_as_test,
            **scoring_definition,
        )
        logger.info(report.response)
        if not run_as_test:
            logger.info(f"{report.response.status_code} " f"{report.response.text}")
        logger.info(f"Created safety_score for {mac_address}")

        logger.info("JSON = {}".format(report.to_json()))
    else:
        logger.info(f"No values to analyze for {mac_address}")

    if run_as_test:
        if em is not None:
            return max(
                em.get_score("AngularActivityScore")[0]
            )  # just put something for now


def _delete_keys(keys, scoring_definition):
    for key in keys:
        if key in scoring_definition:
            del scoring_definition[key]


@dramatiq.actor(periodic=cron("*/2 * * * *"))
def automated_analysis():
    logger.info("Running automated analysis")

    run_interval = int(
        os.getenv("DATA_LOOKBACK_INTERVAL_MINUTES", 15)
    )  # default to using past 15 minutes of data

    current_time = datetime.datetime.utcnow()
    end_time = datetime.datetime.utcnow().isoformat()
    start_time = (current_time - datetime.timedelta(minutes=run_interval)).isoformat()

    # here we can decide which alias to search for:
    run_as_test = bool(os.getenv("RUN_AS_TEST", False))
    from_alias = os.getenv("CASSIA_ALIAS")
    find_alias_among_indexes = os.getenv(
        "CASSIA_ALIAS_INDEX_NAME"
    )  # narrow down search to these index names...
    # ...(for example the start could expand into days)
    host = os.getenv("ELASTIC_SEARCH_HOST")

    index = None
    if from_alias is None:
        # we are not loading via alias, but directly via indexes:
        index = os.getenv("ELASTIC_SEARCH_INDEX")

    bsafe_setup_filename = os.getenv("BSAFE_SETUP_FILENAME")

    logger.info("Here is the env: {}".format(os.environ))
    logger.info("from_alias: {}".format(from_alias))
    logger.info("find_alias_among_indexes: {}".format(find_alias_among_indexes))
    logger.info("host: {}".format(host))
    logger.info("index: {}".format(index))
    logger.info("current time: {}".format(current_time))
    logger.info("analysis start time: {}".format(start_time))
    logger.info("analysis end time: {}".format(end_time))
    logger.info("BSAFE setup filename: {}".format(bsafe_setup_filename))

    try:
        response = api_client.get_request("api/v1/wearables?automated=true")
        response.raise_for_status()
        wearables = response.json()["data"]
        logger.info(f"Running automated analysis for {len(wearables)}")
        for wearable in wearables:
            mac_address = wearable["attributes"]["mac"]
            logger.info(f'Running analysis for wearable with MAC: "{mac_address}"')
            safety_score_analysis.send(
                mac_address,
                start_time,
                end_time,
                host=host,
                index=index,
                from_alias=from_alias,
                find_alias_among_indexes=find_alias_among_indexes,
                run_as_test=run_as_test,
                bsafe_setup_filename=bsafe_setup_filename,
            )
        logger.info(f"Enqueued all analyses")
    except HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}", exc_info=True)
    except Exception as err:
        logger.error(f"Failure to send request {err}", exc_info=True)


def parse_bsafe_setup_file(bsafe_setup_filename=None):
    # LOAD YAML FILE FOR SETTINGS
    if bsafe_setup_filename is None:
        raise ValueError("Scoring Definition Filename is None!")

    bsafe_setup_yaml = bsafe_setup_filename
    if not os.path.isfile(bsafe_setup_yaml):
        msg = "Please provide a valid BSAFE scoring definition file, not '{}'!".format(
            bsafe_setup_yaml
        )
        raise ValueError(msg)

    scoring_definition, scoring_hash = parse_bsafe_yaml(yamlfile=bsafe_setup_yaml)
    return scoring_definition, scoring_hash


@dramatiq.actor(max_retries=3)
def safety_score_analysis(
    mac_address,
    start_time,
    end_time,
    from_alias=None,
    find_alias_among_indexes=None,
    run_as_test=False,
    host=None,
    index=None,
    bsafe_setup_filename=None,
):
    logger.info("Starting function 'safety_score_analysis'")
    logger.info(f"Getting safety score for {mac_address}")

    scoring_definition, scoring_hash = parse_bsafe_setup_file(
        bsafe_setup_filename=bsafe_setup_filename
    )

    data_loader = LoadElasticSearch()
    raw_data = data_loader.retrieve_data(
        mac_address=mac_address,
        start_time=start_time,
        end_time=end_time,
        limit=None,
        from_alias=from_alias,
        find_alias_among_indexes=find_alias_among_indexes,
        index=index,
        host=host,
    )

    run_BSAFE(
        raw_data=raw_data,
        mac_address=mac_address,
        run_as_test=run_as_test,
        with_format_code=data_loader.data_format_code,
        scoring_definition=scoring_definition,
        scoring_hash=scoring_hash,
        bsafe_setup_filename=bsafe_setup_filename,
    )


def run_status():
    """Created to more easily test the status endpoint"""

    data_loader = LoadElasticSearch()
    mac_address, raw_data = data_loader.retrieve_any_macaddress_with_data(
        at_least_this_much_data_in_total=50, return_max_this_much_data=20
    )

    logger.info("Mac address found is: {}".format(mac_address))

    if raw_data is None:
        logger.warning(
            f"/STATUS: Found no elements in the ES database for '{mac_address}' during status check."
        )
        return 500

    scoring_definition, scoring_hash = parse_bsafe_setup_file(
        bsafe_setup_filename="bsafe_run_setup.yml"
    )

    logger.info("Running BSAFE on data!")
    score = run_BSAFE(
        raw_data=raw_data,
        mac_address=mac_address,
        run_as_test=True,
        scoring_definition=scoring_definition,
        scoring_hash=scoring_hash,
        with_format_code=data_loader.data_format_code,
    )

    score_error = False
    if score is None or not 0 <= score <= 7:
        logger.warning("Score could not be computed by BSAFE!")
        score_error = True

    response = {
        "status_code": 500 if score_error else 200,
        "mac_address": mac_address if mac_address else "null",
        "score": score if score else "null",
        "status": "processed",
    }

    return response


@dramatiq.actor(max_retries=3)
def status():
    """Health check: Check that the BSAFE code is functioning properly.

    Used in K8S health check.

    Returns:
        200 (int) if BSAFE works as expected.
        500 (int) if there are issues with BSAFE or the Elastic Search Database.
    """
    return run_status()


if __name__ == "__main__":
    status = run_status()
    print("STATUS IS: {}".format(status))
