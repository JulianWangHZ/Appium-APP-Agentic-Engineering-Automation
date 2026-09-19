"""Base API client — foundation of the hybrid pattern (arrange via API, assert via UI).

Every HTTP call funnels through BaseApiClient.request(): unified timeout,
logging, error context, and auth header. Domain clients inherit and only add
endpoint methods:

    class UserClient(BaseApiClient):
        def create_user(self, email: str, password: str) -> dict:
            return self.post("/v1/users", json={"email": email, "password": password}).json()

Cross-endpoint orchestration belongs in api/workflows.py, not in clients.
"""
from __future__ import annotations

import logging
import os

import requests

from config.settings import Settings

logger = logging.getLogger("framework")

DEFAULT_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))


class ApiError(RuntimeError):
    """HTTP 4xx/5xx with method/url/status/body summary — diagnosable at the point of failure."""

    def __init__(self, response: requests.Response):
        self.response = response
        self.status_code = response.status_code
        body = response.text[:500]
        super().__init__(
            f"{response.request.method} {response.url} -> {response.status_code}: {body}"
        )


class BaseApiClient:
    def __init__(self, settings: Settings, timeout: int = DEFAULT_TIMEOUT):
        self.base_url = settings.api_base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def set_token(self, token: str) -> None:
        self.session.headers["Authorization"] = f"Bearer {token}"

    def request(self, method: str, path: str, *, check: bool = True,
                **kwargs) -> requests.Response:
        """check=False skips raising ApiError — for negative tests that assert
        the status code themselves."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        kwargs.setdefault("timeout", self.timeout)
        response = self.session.request(method, url, **kwargs)
        logger.info("%s %s -> %s", method, url, response.status_code)
        if check and not response.ok:
            raise ApiError(response)
        return response

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs) -> requests.Response:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.request("DELETE", path, **kwargs)
