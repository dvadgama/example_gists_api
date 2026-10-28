import json

import httpx
import pytest

from app.github import GitHubClient


@pytest.fixture
def successful_gists_response(public_gists):
    return httpx.Response(200, json=public_gists)


@pytest.fixture
def empty_gists_response():
    return httpx.Response(200, json=[])


@pytest.fixture(
    params=[b"", b"<html>Not JSON</html>", b'[{"id":'],
    ids=["empty-body", "html-body", "malformed-json"],
)
def invalid_json_response(request):
    return httpx.Response(200, content=request.param)


@pytest.fixture(
    params=[
        None,
        {"message": "Unexpected response"},
        "not a list",
        [None],
        ["not a gist"],
        [[{}]],
    ],
    ids=["null", "object", "string", "null-item", "string-item", "nested-list"],
)
def invalid_gist_list_response(request):
    return httpx.Response(
        200,
        content=json.dumps(request.param),
        headers={"Content-Type": "application/json"},
    )


@pytest.fixture(
    params=[403, 404, 429, 500, 503],
    ids=["forbidden", "not-found", "rate-limited", "server-error", "unavailable"],
)
def upstream_error_response(request):
    return httpx.Response(request.param, text="Upstream error")


@pytest.fixture(
    params=[
        httpx.ConnectTimeout,
        httpx.ReadTimeout,
        httpx.WriteTimeout,
        httpx.PoolTimeout,
    ],
    ids=["connect", "read", "write", "pool"],
)
def timeout_error(request):
    return request.param("Simulated timeout")


@pytest.fixture(
    params=[httpx.ConnectError, httpx.ReadError],
    ids=["connect", "read"],
)
def network_error(request):
    return request.param("Simulated network failure")


@pytest.fixture
def github_client_factory(settings, github_requests):
    http_clients = []

    def create_client(response_or_error):
        def respond(request: httpx.Request) -> httpx.Response:
            github_requests.append(request)
            if isinstance(response_or_error, Exception):
                raise response_or_error
            return response_or_error

        http_client = httpx.Client(
            base_url=settings.github_base_url,
            timeout=settings.github_timeout_seconds,
            transport=httpx.MockTransport(respond),
        )
        http_clients.append(http_client)
        return GitHubClient(http_client)

    yield create_client

    for http_client in http_clients:
        http_client.close()
