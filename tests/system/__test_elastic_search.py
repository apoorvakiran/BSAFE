# -*- coding: utf-8 -*-
"""
Test the Elastic Search implementation in SAFE.

First, start your elastic net server if running locally.
You need to tell elastic search where to find Java by defining the
JAVA_HOME environment variable. One way is to install java with homebrew
(if on Mac) and then ponting to the root of "/bin/java".

Then, for example, if the folder is "elasticsearch-7.3.0",
go to the root of that and then call:
>> ./bin/elasticsearch
this starts the Elastic Net server locally.

Please run "es_load_test_data.py" first to generate the test data
to use with Elastic Search.

To test using staging environment locally

1. install redis and run redis
  - brew install redis
  - run with redis-server or use brew to run in background
(redis-server /usr/local/etc/redis.conf)

2. set all the needed environment variables

create a .env file with the following values and type the command source .env
export SENTRY_DSN=https://4ca7cdcc54274295af09b1f2d98f4960@sentry.io/1728777
export ELASTIC_SEARCH_INDEX=cassia-staging
export AWS_ACCESS_KEY=AKIAXTRZXZRUUGVCREU5
export AWS_SECRET_KEY=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
export ELASTIC_SEARCH_HOST=search-kinesis-cassia-test-ethsitlodguxwer6jtk7uozfkm.us-east-1.es.amazonaws.com
export AWS_REGION=us-east-1
export INFINITY_GAUNTLET_URL=https://staging-api.iteratelabs.co
export INFINITY_GAUNTLET_AUTH=eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxfQ.x2T_qKsO8gSOz2WHLCyFzuf059L2NeH6TtdKX783ZHs
export NO_PROXY=*

3. run applications locally
- requires foreman gem, install ruby, and then install the foreman gem using
gem install foreman

4. run applications
foreman s

5. issue curl request to get safety score and post it
curl "localhost:5000/api/safety_score?mac=F5:12:3D:BD:DE:44&start_time=2019-03-01T00:00:00-05:00&end_time=2019-04-01T00:00:00-05:00"

@ author Iterate Labs, Inc.
Copyright 2018-
"""

__author__ = "Iterate Labs, Inc."
__version__ = "Alpha"

import os
import sys

from ergo_analytics import LoadElasticSearch
from ergo_analytics.filters import FixDateOscillations
from ergo_analytics.filters import DataCentering
from ergo_analytics.filters import ConstructDeltaValues
from ergo_analytics.filters import WindowOfRelevantDataFilter
from ergo_analytics.filters import DataImputationFilter
from ergo_analytics.filters import QuadrantFilter
from ergo_analytics.filters import ZeroShiftFilter
from ergo_analytics import DataFilterPipeline
from ergo_analytics import ErgoMetrics
from ergo_analytics import ErgoReport
from constants import DATA_FORMAT_CODES

import logging

logger = logging.getLogger()

# import json
# # these are just some mac addresses that were created in generating
# # the fake data (just so that we can test it out and grab a random valid one):
# with open(os.path.join(ROOT_DIR, "tests", "system",
#                        "all_device_addresses.json"), "r") as fd:
#   mac_addresses_in_fake_database = json.load(fd)['addresses']

test_address = "F6:12:3D:BD:DE:44"

# def test_retrieve_elastic_search():

index = "iterate-labs-local-poc"

data_format_code = "5"  # in what format is the data coming in?

data_loader = LoadElasticSearch()
raw_data = data_loader.retrieve_data(
    mac_address=test_address,
    start_time="2019-03-18T00:00:00-05:00",
    end_time="2019-03-21T00:00:00-05:00",
    host=None,
    index=index,
    data_format_code=data_format_code,
)

logger.info("Found {} elements in the ES database.".format(len(raw_data)))

# now pass the raw data through our data filter pipeline:
pipeline = DataFilterPipeline()
# instantiate the filters:
pipeline.add_filter(name="fix_osc", filter=FixDateOscillations())
pipeline.add_filter(name="centering1", filter=DataCentering())
pipeline.add_filter(name="delta_values", filter=ConstructDeltaValues())
pipeline.add_filter(name="centering2", filter=DataCentering())
pipeline.add_filter(name="zero_shift_filter", filter=ZeroShiftFilter())
pipeline.add_filter(name="window", filter=WindowOfRelevantDataFilter())
pipeline.add_filter(name="impute", filter=DataImputationFilter())
pipeline.add_filter(name="quadrant_fix", filter=QuadrantFilter())
# run the pipeline!
structured_data = pipeline.run(
    on_raw_data=raw_data,
    with_format_code=data_format_code,
    num_rows_per_chunk=20,
    debug=True,
)

mets = ErgoMetrics(structured_data=structured_data)
mets.compute()
total_score = mets.get_score(name="total")

print("Total score = {}".format(total_score))

report = ErgoReport(ergo_metrics=mets, mac_address=test_address)

print(report)
