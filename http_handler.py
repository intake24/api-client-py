import json
import pathlib
import re

import requests
from requests import Session, Request, Response


class Intake24HttpHandler:
    def __init__(self):
        self.session = Session()
        self.config_dir = pathlib.Path.home() / ".intake24"
        self.config_file = self.config_dir / "api_client.conf"
        self.auth_cache_file = self.config_dir / "auth_cache"

        if not self.config_file.exists():
            raise Exception(f"Please put your Intake24 API configuration into {self.config_file}")

        with open(self.config_file) as json_config_file:
            self.config = json.load(json_config_file)

        if "api_base_url" not in self.config:
            raise Exception("Missing required configuration value: api_base_url")
        else:
            # Drop trailing slash if present to avoid double slashes in formed URLs
            self.api_base_url = re.sub("/+$", "", self.config["api_base_url"])

        if self.auth_cache_file.exists():
            with open(self.auth_cache_file) as f:
                self.refresh_token = f.read()
        else:
            self.refresh_token = None

        self.access_token = None

    def __form_url(self, endpoint: str):
        return self.api_base_url + endpoint

    def __sign_in(self):
        if "username" not in self.config:
            raise Exception("Missing required configuration value: username")

        if "password" not in self.config:
            raise Exception("Missing required configuration value: password")

        response = requests.post(self.__form_url("/signin"),
                                 json={"email": self.config["username"], "password": self.config["password"]},
                                 headers={"content-type": "application/json"})

        response.raise_for_status()

        self.refresh_token = response.json()["refreshToken"]

        with open(self.auth_cache_file, "w") as f:
            f.write(self.refresh_token)

    def __refresh(self):
        if self.refresh_token is None:
            # No cached refresh token available, request a new one
            self.__sign_in()

        response = requests.post(self.__form_url("/refresh"),
                                 headers={"X-Auth-Token": self.refresh_token})

        if response.status_code == 401:
            # Cached refresh token no longer valid, request a new one and retry
            self.__sign_in()

            response = requests.post(self.__form_url("/refresh"),
                                     headers={"X-Auth-Token": self.refresh_token})

        response.raise_for_status()

        self.access_token = response.json()["accessToken"]

    def __send_with_auth(self, request: Request) -> Response:
        if self.access_token is None:
            self.__refresh()

        request.headers.update({"X-Auth-Token": self.access_token})
        prepared = request.prepare()

        response = self.session.send(prepared)

        if response.status_code == 401:
            # Access token expired, clear it (this will cause a refresh) and retry
            self.access_token = None
            return self.send_with_auth(request)
        else:
            return response

    def send_with_auth(self, method: str, endpoint: str, **request_args) -> Response:
        return self.__send_with_auth(Request(method, self.__form_url(endpoint), request_args))
