# -*- coding: utf-8 -*-
"""
Testing the AWS S3 interaction.

The examples on AWS usage are here:
https://docs.aws.amazon.com/code-samples/latest/catalog/python-s3-s3-python-example-upload-file.py.html

@ author Jesper Kristensen
Copyright 2019
"""

__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import os
from Data import upload_data_to_aws_s3, download_from_aws_s3


def test_upload():
    # Let's upload a file to the S3 bucket
    # create a test file:
    os.system("touch data_from_glove_example.txt")

    upload_data_to_aws_s3(bucketname='thisisacoolbucket1234',
                          filename='data_from_glove_example.txt')

    print("Data has been uploaded!")

    # now remove the file locally:
    os.remove("data_from_glove_example.txt")

def test_download():

    local_filename = 'the_data_locally.txt'  # name of file locally

    if os.path.isfile(local_filename):
        os.remove(local_filename)

    download_from_aws_s3(bucketname='thisisacoolbucket1234',
                         filename='data_from_glove_example.txt',
                         local_filename=local_filename)

    assert os.path.isfile(local_filename)
    os.remove(local_filename)  # remove the downloaded file

    print("Data was downloaded correctly!")
