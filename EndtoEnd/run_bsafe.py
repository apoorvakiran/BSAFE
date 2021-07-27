import os
from ergo_analytics.metrics import AngularActivityScore, PostureScore
from productivity import active_score
import pandas as pd
from ergo_analytics import (
    LoadDataFromLocalDisk,
    DataFilterPipeline,
    ErgoMetrics,
    ErgoReport,
)
from ergo_analytics.filters import ConstructDeltaValues, QuadrantFilter
from productivity.active_score import ActiveScore


data_format_code = "5"
test_data_path = os.path.join("Demos/demo-format-5", "prod_data.csv")
test_data = pd.read_csv(test_data_path)

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
delta_only_pipeline.add_filter(name="construct-delta", filter=ConstructDeltaValues())
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
payload = reporter.to_http(just_return_payload=True)

for k in payload:
    print(k, payload[k])
