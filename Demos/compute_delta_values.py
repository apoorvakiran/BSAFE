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

path_to_data = "/Users/jesper/Downloads/Wearable/worker_1_left.csv"
df = pd.read_csv(path_to_data)

df_transformed = pipeline.run(
    on_raw_data=df, with_format_code=with_format_code, use_subsampling=False
)[0].data_matrix
