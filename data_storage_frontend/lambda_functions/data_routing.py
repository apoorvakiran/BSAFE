# -*- coding: utf-8 -*-
"""
Lambda Functions and associated helper functions responsible
for uploading data from the Data Store UI frontend to the backend
server on AWS technology (S3 and Dynamo DB).

@ author Jesper Kristensen
Copyright 2018-
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"


def lambda_data_router_to_store(event, lambda_context):
    """
    This lambda function is responsible for routing data to the
    server from the UI.
    """
    print(event)
    print(lambda_context)
    print("WOOHOO!")
