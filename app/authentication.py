import os
import requests
import logging
from urllib.error import HTTPError
from requests.exceptions import RequestException

logger = logging.getLogger()


class Authentication(object):
    def __init__(self, *, token=None, username=None, password=None):
        self.current_token = token or os.getenv("INFINITY_GAUNTLET_AUTH")
        self.username = username or os.getenv("INFINITY_GAUNTLET_USERNAME")
        self.password = password or os.getenv("INFINITY_GAUNTLET_PASSWORD")

    def get_authentication_header(self):
        self.current_token = self._refresh_token_if_needed()
        return f"Bearer {self.current_token}"

    def _refresh_token_if_needed(self):
        try:
            token_response = self._check_auth()
            if token_response.status_code == 200:
                token = token_response.json()["data"]["attributes"]["auth_token"]
                return token
            else:
                logger.info(f"Re-authenticating with Infinity Gauntlet")
                login_response = self._login()
                if login_response.status_code == 200:
                    token = login_response.json()["data"]["attributes"]["auth_token"]
                    return token
                else:
                    raise Exception(f"Authentication failure: {login_response.json()}")
        except HTTPError as err:  # TODO: handle other errors
            logger.error(f"HTTPError: {err}", exc_info=True)
        except RequestException as err:
            logger.error(f"ConnectionError: {err}", exc_info=True)
        except Exception as err:
            logger.error(f"Failure to authenticate: {err}", exc_info=True)
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
