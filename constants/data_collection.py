# Constants related to the data collection process.
# This relates to the data store interaction.
# 
# Author: Jesper Kristensen
# Copyright Iterate Labs, Inc.

__all__ = ['valid_teams', 'generate_unique_id']

import uuid

# Set of team names that can be used for creating
# buckets in our Data Store (S3):
valid_teams = {"data-science", "software"}


def generate_unique_id():
    """
    Generates a unique ID to use with the bucket name
    when interacting with our bucket store.
    """
    return str(uuid.uuid4())
