"""Framework self-tests: BaseApiClient behavior without network."""
from unittest.mock import MagicMock

import pytest

from api.base_client import ApiError, BaseApiClient
from config.settings import get_settings


@pytest.fixture
def client() -> BaseApiClient:
    get_settings.cache_clear()
    return BaseApiClient(get_settings("android", "staging"))


def _fake_response(status_code: int, method: str = "POST") -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.ok = status_code < 400
    response.text = '{"error": "boom"}'
    response.url = "https://api.staging.example.com/v1/things"
    response.request.method = method
    return response


def test_joins_url_and_sets_timeout(client):
    client.session.request = MagicMock(return_value=_fake_response(200))
    client.get("/v1/things")
    method, url = client.session.request.call_args.args
    assert method == "GET"
    assert url == f"{client.base_url}/v1/things"
    assert client.session.request.call_args.kwargs["timeout"] == client.timeout


def test_error_message_contains_method_url_status_body(client):
    client.session.request = MagicMock(return_value=_fake_response(422))
    with pytest.raises(ApiError, match="POST.*v1/things.*422.*boom"):
        client.post("/v1/things", json={})


def test_check_false_returns_error_response(client):
    client.session.request = MagicMock(return_value=_fake_response(404, method="GET"))
    response = client.get("/v1/missing", check=False)
    assert response.status_code == 404


def test_set_token_adds_bearer_header(client):
    client.set_token("abc123")
    assert client.session.headers["Authorization"] == "Bearer abc123"
