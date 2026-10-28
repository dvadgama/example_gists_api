from unittest.mock import create_autospec

import httpx2
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.github import GitHubClient, InvalidGitHubResponseError
from app.routes import router


@pytest.fixture
def mock_github_client(public_gists):
    client = create_autospec(GitHubClient, instance=True, spec_set=True)
    client.list_public_gists.return_value = public_gists
    return client


@pytest.fixture
def route_app(mock_github_client):
    app = FastAPI()
    app.state.github_client = mock_github_client
    app.include_router(router, prefix="/v1")
    return app


@pytest.fixture
def route_request(route_app):
    return Request({"type": "http", "app": route_app})


@pytest.fixture
def route_client(route_app):
    with TestClient(route_app) as client:
        yield client


@pytest.fixture(
    params=[
        "",
        " ",
        "bad user",
        "../user",
        "user/name",
        "name?query",
        "name#part",
        "a" * 40,
    ],
    ids=[
        "empty",
        "blank",
        "space",
        "traversal",
        "slash",
        "query",
        "fragment",
        "too-long",
    ],
)
def invalid_username(request):
    return request.param


@pytest.fixture(params=["a", "Alice", "user-name", "a" * 39, "mona-cat_octo"])
def valid_username(request):
    return request.param


@pytest.fixture
def upstream_error_factory():
    def create_error(status_code, headers=None, body=None):
        request = httpx2.Request("GET", "https://api.github.com/users/alice/gists")
        response = httpx2.Response(
            status_code, headers=headers, request=request, json=body
        )
        return httpx2.HTTPStatusError(
            "Upstream GitHub error", request=request, response=response
        )

    return create_error


@pytest.fixture(
    params=[
        httpx2.ConnectTimeout,
        httpx2.ReadTimeout,
        httpx2.WriteTimeout,
        httpx2.PoolTimeout,
    ],
    ids=["connect", "read", "write", "pool"],
)
def timeout_error(request):
    return request.param("Simulated timeout")


@pytest.fixture(
    params=[
        httpx2.ConnectError,
        httpx2.ReadError,
        httpx2.RemoteProtocolError,
        httpx2.DecodingError,
    ],
    ids=["connect", "read", "protocol", "decoding"],
)
def transport_error(request):
    return request.param("Simulated upstream failure")


@pytest.fixture
def invalid_response_error():
    return InvalidGitHubResponseError("GitHub returned invalid JSON")


@pytest.fixture(params=[400, 401, 403, 422, 500, 502, 503])
def non_rate_limit_error(request, upstream_error_factory):
    return upstream_error_factory(request.param)


@pytest.fixture(
    params=[{"message": "Forbidden"}, {"message": None}, ["Unexpected error"]]
)
def non_rate_limit_forbidden_error(request, upstream_error_factory):
    return upstream_error_factory(403, body=request.param)


@pytest.fixture(
    params=[
        (429, {}, None),
        (403, {"X-RateLimit-Remaining": "0"}, None),
        (403, {"Retry-After": "60"}, None),
        (403, {}, {"message": "You have exceeded a secondary rate limit."}),
        (403, {}, {"message": "API rate limit exceeded for this address."}),
    ],
    ids=[
        "429",
        "primary-limit",
        "secondary-limit",
        "secondary-message",
        "primary-message",
    ],
)
def rate_limit_error(request, upstream_error_factory):
    status_code, headers, body = request.param
    return upstream_error_factory(status_code, headers, body)


@pytest.fixture(params=["0", "60", "Wed, 01 Jan 2031 00:00:00 GMT"])
def valid_retry_after(request):
    return request.param


@pytest.fixture(
    params=[
        "",
        "-1",
        "1.5",
        "later",
        "Wed, 31 Feb 2031 00:00:00 GMT",
        "Wed, 01 Jan 2031 00:00:00",
        "Wed, 01 Jan 2031 00:00:00 +0000",
        "60\r\nX-Injected: true",
    ],
    ids=[
        "empty",
        "negative",
        "decimal",
        "text",
        "invalid-date",
        "no-timezone",
        "non-http-date",
        "newline",
    ],
)
def invalid_retry_after(request):
    return request.param


@pytest.fixture(params=["/alice", "/v2/alice", "/v1/user/alice/gists"])
def unknown_path(request):
    return request.param


@pytest.fixture(params=["POST", "PUT", "PATCH", "DELETE"])
def unsupported_method(request):
    return request.param
