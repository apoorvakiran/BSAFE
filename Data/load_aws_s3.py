# -*- coding: utf-8 -*-
"""
This file is to demonstrate how to download and upload data
from the AWS S3 buckets.

The data goes from the glove to AWS to SAFE!

@ author Jesper Kristensen
Copyright 2018-
"""

__all__ = ["upload_data_to_aws_s3", "download_from_aws_s3"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import boto3
import botocore


def upload_data_to_aws_s3(bucketname=None, filename=None):
    """
    Uploads the given file using a managed uploader, which will split up large
    files automatically and upload parts in parallel.

    :param bucketname:
    :param filename:
    :return:
    """
    # Create an S3 client
    s3 = boto3.client('s3')
    s3.upload_file(filename, bucketname, filename)


def download_from_aws_s3(bucketname=None, filename=None,
                         local_filename=None):

    if not local_filename:
        local_filename = filename

    s3 = boto3.resource('s3')

    try:
        s3.Bucket(bucketname).download_file(filename, local_filename)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist in the AWS S3 bucket.")
        else:
            raise
