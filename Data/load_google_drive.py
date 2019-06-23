# -*- coding: utf-8 -*-
"""
<THIS CODE IS NOT DONE.> (June 22, 2019)

The Google drive is proving to be a bit difficult at present
to interact with. For now, it's not top priority, so I will
be moving on to another priority.

Loads data from Google drive.

More info on setting up the API:
https://developers.google.com/drive/api/v3/quickstart/python?authuser=1

@ author Jesper Kristensen
Copyright 2018
"""

__all__ = ["LoadGoogleDrive"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

from Data import BaseData


class LoadGoogleDrive(BaseData):

    def __init__(self, local_path=None):

        super().__init__()



        import os
        from pydrive.auth import GoogleAuth
        from pydrive.drive import GoogleDrive
        from oauth2client.client import GoogleCredentials

        # 1. Authenticate and create the PyDrive client.
        gauth = GoogleAuth()
        gauth.credentials = GoogleCredentials.get_application_default()
        drive = GoogleDrive(gauth)

        # choose a local directory to store the data.
        local_download_path = os.path.expanduser('~/{}'.format(local_path))
        try:
            os.makedirs(local_download_path)
        except:
            pass

        import pdb
        pdb.set_trace()
