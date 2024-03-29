"""Shows how to retrieve data from a wearable using Elastic Search.

@author: Jesper Kristensen
Iterate Labs, Inc. All Rights Reserved, Patent Pending
"""

import os
import pandas as pd
from ergo_analytics.data_raw import LoadElasticSearch
from app.tasks import run_BSAFE


# JESPER: DEPRECATED SINCE ATHENA WAS TOO EXPENSIVE FOR NOW
def __test_run_bsafe_on_staging_data():
    # Perform this end-to-end test to make sure BSAFE runs as expected

    # now we download the data:
    data_loader = LoadElasticSearch()
    try:
        mac_address = "C4:E2:D8:DB:4B:48"
        index = os.getenv("ELASTIC_SEARCH_INDEX", "iterate-labs-local-poc")
        host = os.getenv("ELASTIC_SEARCH_HOST")
        start_time = pd.to_datetime("2020-07-14")
        end_time = pd.to_datetime("2020-07-18")

        raw_data = data_loader.retrieve_data(
            mac_address=mac_address,
            start_time=start_time,
            end_time=end_time,
            host=host,
            index=index,
            limit=20,
        )
        if raw_data is None:
            raise Exception("No data!")
    except Exception as _:
        mac_address, raw_data = data_loader.retrieve_any_macaddress_with_data(
            at_least_this_much_data_in_total=200,
            return_max_this_much_data=200,
            force_rerun=True,
        )

    score = run_BSAFE(
        raw_data=raw_data,
        mac_address=mac_address,
        run_as_test=True,
        with_format_code=data_loader.data_format_code,
        bsafe_setup_filename="bsafe_run_setup_test.yml",
    )

    assert score is not None
    assert 0 <= score <= 7
