# -*- coding: utf-8 -*-
"""

@ author Jesper Kristensen
Copyright 2018 Iterate Labs, Inc.
All Rights Reserved. Patent pending.
"""

import pandas as pd
from ergo_analytics import DataFilterPipeline
from ergo_analytics.filters import ConstructDeltaValues


pipeline = DataFilterPipeline(verify_pipeline=False)
pipeline.add_filter(name="construct-delta", filter=ConstructDeltaValues())
with_format_code = "5"

paths = (
    "/Users/jesper/Downloads/Wearable/worker_1_left",
    "/Users/jesper/Downloads/Wearable/worker_1_right",
    "/Users/jesper/Downloads/Wearable/worker_2_left",
    "/Users/jesper/Downloads/Wearable/worker_2_right",
    "/Users/jesper/Downloads/Wearable/worker_3_left",
    "/Users/jesper/Downloads/Wearable/worker_3_right",
)


for path in paths:
    df = pd.read_csv(path + ".csv")

    df_transformed = pipeline.run(
        on_raw_data=df, with_format_code=with_format_code, use_subsampling=False
    )[0].data_matrix

    df_transformed.to_csv(path + "_trans.csv", index=False)
