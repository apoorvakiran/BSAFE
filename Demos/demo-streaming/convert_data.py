"""
Quick converter for the original data to turn it into "delta only"
data.

@author Jesper Kristensen
Copyright Iterate Labs, Inc.
"""
import pandas as pd

data = pd.read_csv('data_for_conversion.csv', header=None)

data = data.iloc[:, :4]
data.to_csv("data_only_deltas.csv", index=False)

data = data.iloc[:100, :]
data.to_csv("data_only_deltas_small.csv", index=False)

