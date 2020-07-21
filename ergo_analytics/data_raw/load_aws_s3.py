# -*- coding: utf-8 -*-
"""

@ author Jesper Kristensen
Copyright IterateLabs.co 2018-
"""

__all__ = ["LoadS3"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import logging
import datetime
import os
import pandas as pd
import s3fs
from ergo_analytics.data_raw import BaseData

logger = logging.getLogger()

fs = s3fs.S3FileSystem(
    anon=False,
    key=os.getenv("BSAFE_AWS_ACCESS_KEY"),
    secret=os.getenv("BSAFE_AWS_SECRET_KEY"),
)


class LoadS3(BaseData):
    """
    Load data from S3.
    """

    def __init__(self):
        """
        Construct the data loader.
        """
        super().__init__()

        logger.info("Data loading with Elastic Search object created!")

    def return_folder_given_time(self, timestamp=None):
        """Given timestamp, return folder prefix on S3."""
        # get year:
        year = timestamp.strftime("%Y")

        # get month:
        month = timestamp.strftime("%m")

        # get day:
        day = timestamp.strftime("%d")

        # get hour:
        hour = timestamp.strftime("%H")

        return "cassia-data/es-backup{}/{}/{}/{}".format(year, month, day, hour)

    def retrieve_data(
        self, mac_address=None, start_time=None, end_time=None, limit=None,
    ):
        """Retrieve wearable data from S3.

        :param mac_address:
        :param start_time:
        :param end_time:
        :param limit: should the number of returned data points be ceiled at limit?
        :return:
        """

        if not start_time or not end_time:
            raise Exception(
                "Please provide both the start_time and the end_time parameters!"
            )

        prev_hour = starttime - datetime.timedelta(hours=1)
        next_hour = starttime + datetime.timedelta(hours=1)

        # get current time +/- 1 hour:
        prev_folder = self.return_folder_given_time(timestamp=prev_hour)
        curr_folder = self.return_folder_given_time(timestamp=starttime)
        next_folder = self.return_folder_given_time(timestamp=next_hour)

        # So only read files from those three prefixes
        # Then use pyarrow to get all that data:
        """
        # Read in user specified partitions of a partitioned parquet file

        import s3fs
        import pyarrow.parquet as pq
        s3 = s3fs.S3FileSystem()

        keys = ['keyname/blah_blah/part-00000-cc2c2113-3985-46ac-9b50-987e9463390e-c000.snappy.parquet'\
                 ,'keyname/blah_blah/part-00001-cc2c2113-3985-46ac-9b50-987e9463390e-c000.snappy.parquet'\
                 ,'keyname/blah_blah/part-00002-cc2c2113-3985-46ac-9b50-987e9463390e-c000.snappy.parquet'\
                 ,'keyname/blah_blah/part-00003-cc2c2113-3985-46ac-9b50-987e9463390e-c000.snappy.parquet']

        bucket = 'bucket_yada_yada_yada'

        # Add s3 prefix and bucket name to all keys in list
        parq_list=[]
        for key in keys:
            parq_list.append('s3://'+bucket+'/'+key)

        # Create your dataframe
        df = pq.ParquetDataset(parq_list, filesystem=s3).read_pandas(columns=['Var1','Var2','Var3']).to_pandas()
"""

        # narrow in: find the files of interest now
        # do a lookup function that takes in the exact time to the minute
        # and returns the file for that +/- 15 min (which may include looking in next/prev folders).
        # We could combine all files together in one list, then just extract the minute marker
        # then bisect on that (since we will have the full file paths its fine to combine)
        files = self.return_files_given_time(
            prev_folder=prev_folder,
            curr_folder=curr_folder,
            next_folder=next_folder,
            start_time=start_time,
            end_time=end_time,
        )

        # finally, extract content from files:

        import pdb

        pdb.set_trace()


if __name__ == "__main__":
    ls = LoadS3()
    endtime = pd.to_datetime("2020-07-15 03:00:00")
    starttime = endtime - datetime.timedelta(minutes=15)
    ls.retrieve_data(
        mac_address="F9:E2:82:9A:55:61", start_time=starttime, end_time=endtime
    )
