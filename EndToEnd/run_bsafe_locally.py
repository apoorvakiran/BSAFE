# -*- coding: utf-8 -*-
"""Run BSAFE locally.

@ author Data Science
Copyright 2018 Iterate Labs, Inc.
All Rights Reserved. Patent pending.
"""

import pandas as pd
from app.tasks import run_BSAFE


# ===== USER INPUTS
path_to_local_data = "EndToEnd/test_data.csv"
# =====

raw_data = pd.read_csv(path_to_local_data)

# let's peek at the data:
print(raw_data.head(10))

# now compute the score
score = run_BSAFE(
    raw_data=raw_data,
    mac_address=None,
    run_as_test=True,
    bsafe_setup_filename="bsafe_run_setup_test.yml",  # this is the yaml setup file we use in production too
)

print(f"The score is: {score}")
