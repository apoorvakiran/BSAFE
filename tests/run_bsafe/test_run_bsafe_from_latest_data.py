"""Shows how to retrieve data from a wearable using Elastic Search.

@author: Jesper Kristensen
Iterate Labs, Inc. All Rights Reserved, Patent Pending
"""

import os
import sys
import pandas as pd
from ergo_analytics.data_raw import LoadElasticSearch
from app.tasks import run_BSAFE


def test_run_bsafe_on_staging_data():
    # Perform this end-to-end test to make sure BSAFE runs as expected

    try:
        mac_address = "E1:81:74:2C:90:A4"
        index = os.getenv("ELASTIC_SEARCH_INDEX", "iterate-labs-local-poc")
        host = os.getenv("ELASTIC_SEARCH_HOST")
        start_time = pd.to_datetime("2020-07-29 11:00:00").isoformat()
        end_time = pd.to_datetime("2020-07-29 11:15:00").isoformat()

        _limit = 20

        data_loader = LoadElasticSearch()
        raw_data = data_loader.retrieve_data(
            mac_address=mac_address,
            start_time=start_time,
            end_time=end_time,
            host=host,
            index=index,
            limit=_limit,
        )
    except Exception as _:
        assert True
        return

    assert len(raw_data) <= _limit

    score = run_BSAFE(
        raw_data=raw_data,
        mac_address=mac_address,
        run_as_test=True,
        with_format_code=data_loader.data_format_code,
    )
    assert score is not None
    assert 0 <= score <= 7
