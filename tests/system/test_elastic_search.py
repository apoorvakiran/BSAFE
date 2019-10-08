# -*- coding: utf-8 -*-
"""
Test the Elastic Search implementation in SAFE.

Please run "es_load_test_data.py" first to generate the test data
to use with Elastic Search.

To test using staging environment locally

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
export ELASTIC_SEARCH_HOST=https://search-kinesis-cassia-test-ethsitlodguxwer6jtk7uozfkm.us-east-1.es.amazonaws.com
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
curl "localhost:5000/api/safety_score?mac=F5:12:3D:BD:DE:44&from_date=2019-03-01T00:00:00-05:00&till_date=2019-04-01T00:00:00-05:00"

@ author Iterate Labs, Inc.
Copyright 2018-
"""

__author__ = "Iterate Labs, Inc."
__version__ = "Alpha"

import json
from ergo_analytics import ErgoMetrics

# these are just some mac addresses that were created in generating
# the fake data (just so that we can test it out and grab a random valid one):
with open("all_device_addresses.json", "r") as fd:
  mac_addresses_in_fake_database = json.load(fd)['addresses']

# doesn't matter which exact address - just to test - so take the first:
####JACOB - Pulled in a test case data file, assigned address
test_address = 'F6:12:3D:BD:DE:44'
# test_address = mac_addresses_in_fake_database[0]


# def test_retrieve_elastic_search():

"""
Test that we can retrieve data from elastic search and put in SAFE
format for further downstream processing (metrics, reporter, ...).
"""
index = "iterate-labs-local-poc"



import pdb
pdb.set_trace()



es_safe_data = StructuredDataStreaming(streaming_source='elastic_search',
                                       streaming_settings=
                                       {"mac_address": test_address,
                                        "from_date": '2019-09-28T00:00:00-05:00',
                                        "till_date": '2019-10-02T00:00:00-05:00',
                                        "host": None, "index": index},
                                       data_format_code='4')
# *note* the "streaming settings". This argument will be passed on to
# the specific streamer in question...
print("Data Loaded from Streaming:")
#print(es_safe_data.get_data())
#print(es_safe_data.pitch())
mets = ErgoMetrics(es_safe_data)
print(mets._strain)

# test_retrieve_elastic_search()
print("All done!")
