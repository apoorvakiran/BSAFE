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

names = [
    "8D_B8_0.csv",
    "8D_B8_1.csv",
    "8D_B8_2.csv",
    "8D_B8_3.csv",
    "8D_B8_4.csv",
    "8D_B8_5.csv",
    "8D_B8_6.csv",
    "8D_B8_7.csv",
    "8D_B8_8.csv",
    "8D_B8_9.csv",
    "8D_B8_10.csv",
    "8D_B8_11.csv",
    "8D_B8_12.csv",
    "8D_B8_13.csv",
    "8D_B8_14.csv",
    "8D_B8_15.csv",
    "8D_B8_16.csv",
    "8D_B8_17.csv",
    "8D_B8_18.csv",
    "8D_B8_19.csv",
    "8D_B8_20.csv",
]
for i in range(0, len(names)):

    data_format_code = "5"
    test_data_path = os.path.join("Demos/real_data", "demo", names[i])
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
    payload = reporter.to_http(just_return_payload=True)

    print(names[i])
    for k in payload:
        print(k, payload[k])
    print(" ")
