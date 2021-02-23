# -*- coding: utf-8 -*-
"""

@ author Jesper Kristensen
Copyright 2018 Iterate Labs, Inc.
All Rights Reserved. Patent pending.
"""

import pandas as pd
from ergo_analytics import DataFilterPipeline
from ergo_analytics.filters import ConstructDeltaValues

delta_only_pipeline = DataFilterPipeline(verify_pipeline=False)
delta_only_pipeline.add_filter(name="construct-delta", filter=ConstructDeltaValues())
with_format_code = "5"

paths = (
    "/Users/jesper/Downloads/Wearable/worker_1_left",
    "/Users/jesper/Downloads/Wearable/worker_1_right",
    "/Users/jesper/Downloads/Wearable/worker_2_left",
    "/Users/jesper/Downloads/Wearable/worker_2_right",
    "/Users/jesper/Downloads/Wearable/worker_3_left",
    "/Users/jesper/Downloads/Wearable/worker_3_right",
)

paths2 = [
    '/Users/zhangci/Desktop/Iteratelabs/jbs_data/jbs_data_dec1_C8:72:6D:97:8D:B8.csv',
    '/Users/zhangci/Desktop/Iteratelabs/jbs_data/jbs_data_dec1_D0:B6:B3:8E:30:4F.csv',
    '/Users/zhangci/Desktop/Iteratelabs/jbs_data/jbs_data_dec1_D7:AB:47:72:0E:06.csv',
    '/Users/zhangci/Desktop/Iteratelabs/jbs_data/jbs_data_dec1_DD:91:CE:0D:51:79.csv',
    '/Users/zhangci/Desktop/Iteratelabs/jbs_data/jbs_data_dec1_E5:C3:95:FC:D2:2A.csv'
]

for path in paths2:
    df = pd.read_csv(path)

    df_transformed = delta_only_pipeline.run(
        on_raw_data=df, with_format_code=with_format_code, use_subsampling=False
    )[0].data_matrix

    df_transformed.to_csv(path[:-4] + "_trans.csv", index=False)
