import os
from ergo_analytics.metrics import AngularActivityScore, PostureScore
from productivity import active_score
from app.api_client import ApiClient

import pandas as pd
from ergo_analytics import (
    LoadDataFromLocalDisk,
    DataFilterPipeline,
    ErgoMetrics,
    ErgoReport,
)
from ergo_analytics.filters import ConstructDeltaValues, QuadrantFilter
from productivity.active_score import ActiveScore
import argparse
parser = argparse.ArgumentParser(description='Bsafe')
parser.add_argument('pos_arg', type=str,
                    help='S3 Data File Location')

args = parser.parse_args()
api_client = ApiClient()


#file = 's3://sqs-asg-s3bucket-1mdwlg73hw49m/raw/2021/04/14/F9:9D:BD:50:ED:23/F9:9D:BD:50:ED:23_2021314_13'
file = args.pos_arg
mac_address = file.split('/')[-1].split('_')[0]
run_as_test = bool(os.getenv("RUN_AS_TEST", False))

data_format_code = "5"
test_data = pd.read_csv(file,names=["Date-Time","Yaw[0](deg)","Pitch[0](deg)","Roll[0](deg)","Yaw[1](deg)","Pitch[1](deg)","Roll[1](deg)"])

#
pipeline = DataFilterPipeline()
pipeline.add_filter(name="construct-delta", filter=ConstructDeltaValues())
pipeline.add_filter(name="quadrant", filter=QuadrantFilter())

list_of_structured_data_chunks = pipeline.run(
    on_raw_data=test_data,
    with_format_code=data_format_code,
    is_sorted=True,
    use_subsampling=True,
    subsample_size_index=600,
    number_of_subsamples=15,
    randomize_subsampling=False,
)

delta_only_pipeline = DataFilterPipeline(verify_pipeline=False)
delta_only_pipeline.add_filter(
    name="construct-delta", filter=ConstructDeltaValues()
)
structured_all_data = delta_only_pipeline.run(
    on_raw_data=test_data, with_format_code=data_format_code, use_subsampling=False,
)[0].data_matrix

metrics = ErgoMetrics(
    list_of_structured_data_chunks=list_of_structured_data_chunks,
    structured_all_data=structured_all_data,
)

metrics.add(AngularActivityScore)
metrics.add(PostureScore)
metrics.compute()

reporter = ErgoReport(ergo_metrics=metrics)

# test that we are sending the correct format:
payload = reporter.to_http(api_client=api_client,
            mac_address=mac_address,
            run_as_test=run_as_test,)

print(file)
print(payload)

#for k in payload:
#    print(k, payload[k])
#print(" ")
