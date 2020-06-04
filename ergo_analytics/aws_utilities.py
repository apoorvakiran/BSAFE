# -*- coding: utf-8 -*-
"""AWS utilities.

@ author Jesper Kristensen with Iterate Labs, Inc.
Copyright 2018 Iterate Labs, Inc.
All Rights Reserved.
"""

__all__ = ["Pipestore"]
__author__ = "Iterate Labs, Inc."
__version__ = "Alpha"

import boto3
from botocore.errorfactory import ClientError
import pickle
import io
import os
import logging

logger = logging.getLogger()


class Pipestore(object):
    """Here we can interact with the S3 bucket where we hold runs such as those
    from data pipelines."""

    _bucket_name = "pipestore.iteratelabs.co"

    def delete_data(self, hash=None):
        """Delete all data under given hash."""
        bucket = self._get_s3_resource().Bucket(self._bucket_name)
        bucket.objects.filter(Prefix=self._return_folder(hash=hash)).delete()

    def _get_s3_client(self):
        """Return S3 object in form of a client."""
        client = boto3.client(
            "s3",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_KEY"),
        )
        return client

    def _get_s3_resource(self):
        """Returns S3 object in form of a resource."""
        return boto3.resource(
            "s3",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_KEY"),
        )

    def _check_if_data_exists(self, path=None):
        """Let's see if the data exists."""
        try:
            self._get_s3_client().head_object(Bucket=self._bucket_name, Key=path)
            return True
        except ClientError:
            # Not found
            return False

    def upload_data(self, hash=None, data=None, metadata=None):
        """Upload data under a given hash in the pipestore."""

        path = self._return_path(hash=hash)
        s3o = self._get_s3_resource().Object(self._bucket_name, path)

        if metadata is not None:
            response = s3o.put(Body=data, Metadata=metadata)
        else:
            response = s3o.put(Body=data)

        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    def _return_folder(self, hash=None):
        """Return folder given hash."""
        return "data_pipeline" + "/" + hash + "/"

    def _return_path(self, hash=None):
        """Returns path to data on S3 given hash."""
        return self._return_folder(hash=hash) + "pipeline_results.pkl"

    def _download(self, path=None):
        """Download data from S3."""

        obj = self._get_s3_resource().Object(bucket_name=self._bucket_name, key=path)
        buffer = io.BytesIO(obj.get()["Body"].read())
        return pickle.loads(buffer.read())

    def pipestore_hash_exists(self, hash=None):
        """Check if hash is present in the pipestore."""

        path = self._return_path(hash=hash)
        data_exists = self._check_if_data_exists(path=path)

        exists = False
        data = None
        if data_exists:
            # download the data
            exists = True

            data = self._download(path=path)

        return exists, data
