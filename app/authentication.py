import os
import requests
import logging

logger = logging.getLogger()


def auth_success(response):
    return response.status_code == 200


def response_token(response):
    return response.json()["data"]["attributes"]["auth_token"]


class Authentication(object):
    def __init__(self, *, token=None, username=None, password=None):
        self.current_token = token or os.getenv("INFINITY_GAUNTLET_AUTH")
        self.username = username or os.getenv("INFINITY_GAUNTLET_USERNAME")
        self.password = password or os.getenv("INFINITY_GAUNTLET_PASSWORD")

    def get_authentication_header(self):
        # TODO: Refactor so that refreshing happens only when auth token expires
        self.current_token = self._refresh_token_if_needed()
        return f"Bearer {self.current_token}"

    def _refresh_token_if_needed(self):
        try:
            check_auth_response = self._check_auth()
            if auth_success(check_auth_response):
                return response_token(check_auth_response)
            else:
                logger.info(f"Re-authenticating with Infinity Gauntlet")
                login_response = self._login()
                if auth_success(login_response):
                    return response_token(login_response)
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
