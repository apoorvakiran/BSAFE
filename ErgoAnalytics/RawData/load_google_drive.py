# -*- coding: utf-8 -*-
"""
*NOTE*
<THIS CODE IS NOT DONE.> (June 22, 2019)
*NOTE*

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

import requests
from . import BaseData


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

    def download_from_google_drive(self, path=None, destination=None):
        """

        :param path:
        :param destination:
        :return:
        """

        file_id = self.get_id(path)
        URL = "https://docs.google.com/uc?export=download"
        session = requests.Session()

        response = session.get(URL, params={'id': file_id}, stream=True)
        token = self.get_confirm_token(response)

        if token:
            params = {'id': id, 'confirm': token}
            response = session.get(URL, params=params, stream=True)

        self.save_response_content(response, destination)

        return destination

    def get_confirm_token(self, response=None):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(self, response=None, destination=None):

        CHUNK_SIZE = 32768

        print("Storing file to disk...")
        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        print("Done storing to disk!")

    @staticmethod
    def get_id(full_url=None):

        if full_url is None:
            raise Exception("The URL is None! Please provide a valid URL!")

        return full_url.split('id')[1][1:]
