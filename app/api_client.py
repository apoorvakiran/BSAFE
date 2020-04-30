import os
import requests
import logging

API_URL = os.getenv("INFINITY_GAUNTLET_URL")

logger = logging.getLogger()


def auth_success(response):
    return response.status_code == 200


def token_from_response(response):
    return response.json()["data"]["attributes"]["auth_token"]


class ApiClient(object):
    def __init__(self, *, token=None, username=None, password=None):
        self.current_token = token or os.getenv("INFINITY_GAUNTLET_AUTH")
        self.username = username or os.getenv("INFINITY_GAUNTLET_USERNAME")
        self.password = password or os.getenv("INFINITY_GAUNTLET_PASSWORD")

    def get_request(self, endpoint, *, retry=True):
        response = requests.get(
            f"{API_URL}/{endpoint}", headers=self._get_authentication_headers()
        )
        if response.status_code == 401 and retry:
            self._refresh_token()
            return self.get_request(endpoint, retry=False)
        return response

    def post_request(self, endpoint, data, *, retry=True):
        response = requests.post(
            f"{os.getenv('INFINITY_GAUNTLET_URL')}/{endpoint}",
            headers=self._get_authentication_headers(),
            data=data,
        )
        if response.status_code == 401 and retry:
            self._refresh_token()
            return self.post_request(endpoint, data, retry=False)
        return response

    def _get_authentication_headers(self):
        return {"Authorization": f"Bearer {self.current_token}"}

    def _refresh_token(self):
        try:
            logger.info(f"Re-authenticating with Infinity Gauntlet")
            login_response = self._login()
            if auth_success(login_response):
                self.current_token = token_from_response(login_response)
            else:
                raise Exception(f"Authentication failure: {login_response.json()}")
        except Exception as err:
            logger.error(f"Authentication failure: {err}", exc_info=True)
            raise Exception(f"Authentication failure: {err}")

    def _check_auth(self):
        header = f"Bearer {self.current_token}"
        response = requests.get(
            f"{os.getenv('INFINITY_GAUNTLET_URL')}/api/v1/auth/session",
            headers={"Authorization": header},
        )
        return response

    def _login(self):
        response = requests.post(
            f"{os.getenv('INFINITY_GAUNTLET_URL')}/api/v1/auth/login",
            data={"email": self.username, "password": self.password},
        )
        return response
