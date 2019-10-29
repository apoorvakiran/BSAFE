import os
import elasticsearch
from elasticsearch_dsl import Search
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from constants import DATA_FORMAT_CODES
import pandas as pd
import numpy as np

start_time = '2019-10-28T22:35:00Z'
end_time = '2019-10-28T22:45:00Z'
mac_address="F3:A8:7A:9E:6A:6F"
index = 'cassia-staging'
host = 'search-kinesis-cassia-test-ethsitlodguxwer6jtk7uozfkm.us-east-1.es.amazonaws.com'
awsauth = AWS4Auth('AKIAXTRZXZRUUGVCREU5','3h2BOZmyNs1KDcMDxA/y9wjfl/xRQ0Xq1g060dTH','us-east-1', 'es')
es = Elasticsearch(hosts=[{'host': host, 'port': 443}],http_auth=awsauth,use_ssl=True,verify_certs=True,connection_class=RequestsHttpConnection)
search = Search(using=es, index=index).query("match",device__keyword=mac_address).query("range",**{"timestamp": {"gte": start_time,"lte": end_time}}).sort("timestamp")

all_values = []
for hit in search.params(preserve_order=True).scan():

    values = hit['value'].split(',')
    values[-1] = values[-1].rsplit('\r\n')[0]
    values = list(map(float, values))

    timestamp = hit['timestamp']

    values = [timestamp] + values

    all_values.append(values)

raw_data = pd.DataFrame(data=all_values)

data_format_code = '5'

data_column_names = DATA_FORMAT_CODES[data_format_code]['NAMES']
raw_data.columns = data_column_names

data_column_types = DATA_FORMAT_CODES[data_format_code]['TYPES']

raw_data = raw_data.astype(dict(zip(data_column_names,
                                    data_column_types)))

from ergo_analytics import DataFilterPipeline
from ergo_analytics import ErgoMetrics
from ergo_analytics.filters import FixDateOscillations
from ergo_analytics.filters import DataCentering
from ergo_analytics.filters import ConstructDeltaValues
from ergo_analytics.filters import WindowOfRelevantDataFilter
from ergo_analytics.filters import DataImputationFilter
from ergo_analytics.filters import QuadrantFilter
from ergo_analytics.filters import ZeroShiftFilter

# now pass the raw data through our data filter pipeline:
pipeline = DataFilterPipeline()
# instantiate the filters:
pipeline.add_filter(name='fix_osc', filter=FixDateOscillations())
pipeline.add_filter(name='centering1', filter=DataCentering())
pipeline.add_filter(name='delta_values', filter=ConstructDeltaValues())
pipeline.add_filter(name='centering2', filter=DataCentering())
pipeline.add_filter(name='zero_shift', filter=ZeroShiftFilter())
pipeline.add_filter(name='window', filter=WindowOfRelevantDataFilter())
pipeline.add_filter(name='impute', filter=DataImputationFilter())
pipeline.add_filter(name='quadrant_fix', filter=QuadrantFilter())
# run the pipeline!
structured_data = pipeline.run(on_raw_data=raw_data,
                               with_format_code=data_format_code,
                               num_rows_per_chunk=1000,
                               debug=True)

metrics = ErgoMetrics(structured_data=structured_data)
metrics.compute()

"""
Get the data and use what James was running:
mac=F2:2D:78:AD:55:7E

start_time=2019-10-28T23:40:00Z&end_time=2019-10-28T23:46:00Z
start_time=2019-10-29T00:45:00Z&end_time=2019-10-29T00:47:00Z
start_time=2019-10-29T00:36:00Z&end_time=2019-10-29T00:41:00Z 
"""
