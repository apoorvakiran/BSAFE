# -*- coding: utf-8 -*-
"""
This file is to demonstrate how to download and upload data
from the AWS S3 buckets.

To run open a terminal and type:
    >> python test_aws.py

============================================================
Here are instructions on how to create and download the
correct credentials to access the S3 bucket:
============================================================
First, you need to make sure your credentials are correct. These credentials are
like your own set of keys to access the bucket. So each member need their own set of keys.

This is done by creating a folder ".aws" in your home directory. Open your terminal and
type this command:
    >> mkdir ~/.aws

Then also create the file "credentials" (note: no extension needed):
    >> vim ~/.aws/credentials

This opens up VI (use whatever other editor you want - I like VIM).
In the file, please put the following three lines:
[default]
aws_access_key_id = <your access key - get this from AWS>
aws_secret_access_key = <your secret key - get this from AWS>

Note the stuff inside the "<>" brackets: These are keys you need to obtain from AWS and they are
personal to you. To get them sign in to your AWS console then go to the top right under "security credentials".
Look under "Access keys for CLI, SDK, & API access" where you will be able to create and download your keys.

So an example of the three lines is:
[default]
aws_access_key_id = ga3kadlgjrhap495
aws_secret_access_key = dWaFiwaiawFgpa391295D8

In conclusion, this script shows us how the data goes from the glove to AWS and now to SAFE!
Questions? Contact Jesper Kristensen or James Russo.

@ author Jesper Kristensen
Copyright IterateLabs.co 2018-
"""

__all__ = ["create_s3_bucket", "get_existing_bucket_names",
           "upload_data_to_aws_s3", "download_from_aws_s3"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import logging
import boto3
import botocore
from boto3.exceptions import S3UploadFailedError

logger = logging.getLogger()


def _get_s3_client():
    """
    Common code for retrieving the S3 client associated
    with your AWS account.
    """
    client = boto3.client('s3')
    return client


def create_s3_bucket(bucketname=None):
    """
    Creates a new S3 bucket.
    """
    s3 = _get_s3_client()
    s3.create_bucket(Bucket=bucketname)
    logger.debug(f"Bucket '{bucketname}' created successfully!")


def get_existing_bucket_names():
    """
    Retrieve a list of existing bucket names
    from the AWS account.
    """
    # Retrieve the list of existing buckets
    s3 = _get_s3_client()
    response = s3.list_buckets()

    # Output the bucket names
    bucket_names = response['Buckets']
    logger.debug('Existing buckets on S3:')
    logger.debug(bucket_names)

    return response['Buckets']


def upload_data_to_aws_s3(bucketname=None, name_on_s3=None,
                          local_filename=None):
    """
    Uploads the given file using a managed uploader, which will split up large
    files automatically and upload parts in parallel.

    :param bucketname:
    :param filename:
    :return:
    """
    # Create an S3 client
    s3 = _get_s3_client()

    try:
        s3.upload_file(local_filename, bucketname, name_on_s3)
    except S3UploadFailedError as e:
        # something did not work!
        msg = "There was an error uploading the file to the S3 bucket!\n" \
              "The error is: {}\nDo you have the latest up-to-date\n" \
              "local ~/.aws/credentials file?".format(e)
        logger.exception(msg)
        raise Exception(msg)


def download_from_aws_s3(bucketname=None, s3_name=None, local_filename=None):
    """
    Downloads a file from AWS S3 to local disk.
    """

    if not local_filename:
        local_filename = s3_name

    s3 = _get_s3_client()

    try:
        s3.download_file(bucketname, s3_name, local_filename)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist in the AWS S3 bucket.")
        else:
            # something did not work!
            print("There was an error downloading the file to the S3 bucket!")
            print("The error is: {}".format(e))
            print("Did you update your local ~/.aws/credentials file?")
            raise
