# -*- coding: utf-8 -*-
"""
Testing the Iterate Labs Co AWS S3 interaction with SAFE.
Doing things locally for now, but next step is to put SAFE on AWS as
well in a kind of EC2 instance and have everything work in the cloud!

The examples on AWS usage are here:
https://docs.aws.amazon.com/code-samples/latest/catalog/python-s3-s3-python-example-upload-file.py.html

@ author Jesper Kristensen
Copyright Iterate Labs, Co. 2018-
"""

__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import os
from Data import upload_data_to_aws_s3, download_from_aws_s3

# put the bucket name here:
BUCKET_NAME = 'testbucketjesperkristensen'
# FYI this is a test bucket that I, Jesper, created under Iterate Lab's S3 account.


def test_upload():
    # Let's upload a file to the S3 bucket
    # create a test file (any file for now):
    os.system("touch data_from_glove_example.txt")

    upload_data_to_aws_s3(bucketname=BUCKET_NAME,
                          filename='data_from_glove_example.txt')

    print("Data has been uploaded!")
    # now remove the file locally:
    os.remove("data_from_glove_example.txt")

    # at this point, we can upload to the bucket!

def test_download():

    local_filename = 'the_data_locally.txt'  # name of file locally

    if os.path.isfile(local_filename):
        os.remove(local_filename)

    download_from_aws_s3(bucketname=BUCKET_NAME,
                         filename='data_from_glove_example.txt',
                         local_filename=local_filename)

    assert os.path.isfile(local_filename)
    os.remove(local_filename)  # remove the downloaded file

    print("Data was downloaded correctly!")
    # at this point we can download the data from the bucket!
