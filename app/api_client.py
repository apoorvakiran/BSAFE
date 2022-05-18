import os
import requests
import logging

logger = logging.getLogger()


def api_url():
    return os.getenv("INFINITY_GAUNTLET_URL")

def token_from_response(response):
    return response.json()["data"]["attributes"]["auth_token"]


class ApiClient(object):
    def get_request(self, endpoint, *, retry=True):
        response = requests.get(
            f"{api_url()}/{endpoint}"
        )
        if response.status_code == 401 and retry:
            return self.get_request(endpoint, retry=False)
        return response

    def post_request(self, endpoint, data, *, retry=True):
        response = requests.post(
            f"{api_url()}/{endpoint}",
            data=data,
        )
        if response.status_code == 401 and retry:
            return self.post_request(endpoint, data, retry=False)
        return response
