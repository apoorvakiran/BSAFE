import os
import requests
import logging

logger = logging.getLogger()


def api_url():
    logger.debug("INFINITY_GAUNTLET_URL"+os.getenv("INFINITY_GAUNTLET_URL"))
    return os.getenv("INFINITY_GAUNTLET_URL")

def token_from_response(response):
    return response.json()["data"]["attributes"]["auth_token"]


class ApiClient(object):
    def get_request(self, endpoint, *, retry=True):
        logger.debug("++++++++++++++++++++++++endpoint=" + f"{api_url()}/{endpoint}")
        response = requests.get(
            f"{api_url()}/{endpoint}"
        )
        if response.status_code == 401 and retry:
            return self.get_request(endpoint, retry=False)
        return response

    def post_request(self, endpoint, data, *, retry=True):
        logger.debug("++++++++++++++++++++++++endpoint=" + f"{api_url()}/{endpoint}")
        logger.debug(data)
        logger.debug("++++++++++++++++++++++++")

        response = requests.post(
            f"{api_url()}/{endpoint}",
            data=data,
        )
        if (response.status_code == 401 or response.status_code == 404) and retry:
            return self.post_request(endpoint, data, retry=False)
        return response
