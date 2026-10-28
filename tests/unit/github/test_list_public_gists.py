import httpx
import pytest

from app.github import InvalidGitHubResponseError


@pytest.mark.mock
def test_lists_public_gists_for_user(
    github_client, public_gists, github_requests, settings
):
    result = github_client.list_public_gists("octocat")

    assert result == public_gists
    assert len(github_requests) == 1
    request = github_requests[0]
    assert request.method == "GET"
    assert str(request.url) == (
        f"{settings.github_base_url.rstrip('/')}/users/octocat/gists"
    )
    assert "authorization" not in request.headers
    assert request.extensions["timeout"] == {
        "connect": settings.github_timeout_seconds,
        "read": settings.github_timeout_seconds,
        "write": settings.github_timeout_seconds,
        "pool": settings.github_timeout_seconds,
    }


@pytest.mark.mock
def test_returns_empty_list_when_user_has_no_public_gists(
    github_client, public_gists, github_requests
):
    public_gists.clear()

    result = github_client.list_public_gists("octocat")

    assert result == []
    assert len(github_requests) == 1


@pytest.mark.mock
@pytest.mark.parametrize(
    "github_response",
    [
        httpx.Response(200, content=b""),
        httpx.Response(200, text="<html>Not JSON</html>"),
        httpx.Response(200, text='[{"id":'),
    ],
    ids=["empty-body", "html-body", "malformed-json"],
    indirect=True,
)
def test_rejects_invalid_json(github_client, github_response, github_requests):
    with pytest.raises(InvalidGitHubResponseError, match="invalid JSON"):
        github_client.list_public_gists("octocat")

    assert len(github_requests) == 1


@pytest.mark.mock
@pytest.mark.parametrize(
    "github_response",
    [
        httpx.Response(200, content=b"null"),
        httpx.Response(200, json={"message": "Unexpected response"}),
        httpx.Response(200, json="not a list"),
        httpx.Response(200, json=[None]),
        httpx.Response(200, json=["not a gist"]),
        httpx.Response(200, json=[[{}]]),
    ],
    ids=["null", "object", "string", "null-item", "string-item", "nested-list"],
    indirect=True,
)
def test_rejects_invalid_gist_list(github_client, github_response, github_requests):
    with pytest.raises(InvalidGitHubResponseError, match="invalid Gist list"):
        github_client.list_public_gists("octocat")

    assert len(github_requests) == 1


@pytest.mark.mock
@pytest.mark.parametrize(
    "github_response",
    [
        httpx.Response(status, text="Upstream error")
        for status in [403, 404, 429, 500, 503]
    ],
    ids=["forbidden", "not-found", "rate-limited", "server-error", "unavailable"],
    indirect=True,
)
def test_preserves_upstream_http_error(github_client, github_response, github_requests):
    with pytest.raises(httpx.HTTPStatusError) as caught:
        github_client.list_public_gists("octocat")

    assert caught.value.response is github_response
    assert len(github_requests) == 1


@pytest.mark.mock
@pytest.mark.parametrize(
    "github_response",
    [
        httpx.ConnectTimeout("Simulated connect timeout"),
        httpx.ReadTimeout("Simulated read timeout"),
        httpx.WriteTimeout("Simulated write timeout"),
        httpx.PoolTimeout("Simulated pool timeout"),
    ],
    ids=["connect", "read", "write", "pool"],
    indirect=True,
)
def test_preserves_timeout_without_retry(
    github_client, github_response, github_requests
):
    with pytest.raises(httpx.TimeoutException) as caught:
        github_client.list_public_gists("octocat")

    assert caught.value is github_response
    assert len(github_requests) == 1


@pytest.mark.mock
@pytest.mark.parametrize(
    "github_response",
    [
        httpx.ConnectError("Simulated connection failure"),
        httpx.ReadError("Simulated read failure"),
    ],
    ids=["connect", "read"],
    indirect=True,
)
def test_preserves_network_error_without_retry(
    github_client, github_response, github_requests
):
    with pytest.raises(httpx.NetworkError) as caught:
        github_client.list_public_gists("octocat")

    assert caught.value is github_response
    assert len(github_requests) == 1
