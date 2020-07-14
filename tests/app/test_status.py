# -*- coding: utf-8 -*-
"""Test status endpoint.

@ author Jesper Kristensen
Copyright 2018 Iterate Labs, Inc.
All Rights Reserved. Patent pending.
"""

from ergo_analytics import LoadElasticSearch

data_format_code = "5"  # determined automatically in the data loader if incorrect

data_loader = LoadElasticSearch()
mac_address, raw_data = data_loader.retrieve_any_macaddress_with_data()

print(mac_address)
print(raw_data)
