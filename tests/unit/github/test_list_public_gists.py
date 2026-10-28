import logging

import httpx2
import pytest

from app.github import InvalidGitHubResponseError


@pytest.mark.mock
def test_lists_public_gists_for_user(
    github_client_factory,
    successful_gists_response,
    public_gists,
    github_requests,
    settings,
):
    github_client = github_client_factory(successful_gists_response)

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
    github_client_factory, empty_gists_response, github_requests
):
    github_client = github_client_factory(empty_gists_response)

    result = github_client.list_public_gists("octocat")

    assert result == []
    assert len(github_requests) == 1


@pytest.mark.mock
def test_rejects_invalid_json(
    github_client_factory, invalid_json_response, github_requests, app_logs
):
    github_client = github_client_factory(invalid_json_response)

    with pytest.raises(InvalidGitHubResponseError, match="invalid JSON"):
        github_client.list_public_gists("octocat")

    assert len(github_requests) == 1
    assert app_logs.records[-1].getMessage() == "GitHub returned invalid JSON"
    assert app_logs.records[-1].levelno == logging.ERROR


@pytest.mark.mock
def test_rejects_invalid_gist_list(
    github_client_factory, invalid_gist_list_response, github_requests, app_logs
):
    github_client = github_client_factory(invalid_gist_list_response)

    with pytest.raises(InvalidGitHubResponseError, match="invalid Gist list"):
        github_client.list_public_gists("octocat")

    assert len(github_requests) == 1
    assert app_logs.records[-1].getMessage() == "GitHub returned an invalid Gist list"
    assert app_logs.records[-1].levelno == logging.ERROR


@pytest.mark.mock
def test_preserves_upstream_http_error(
    github_client_factory, upstream_error_response, github_requests, app_logs
):
    github_client = github_client_factory(upstream_error_response)

    with pytest.raises(httpx2.HTTPStatusError) as caught:
        github_client.list_public_gists("octocat")

    assert caught.value.response is upstream_error_response
    assert len(github_requests) == 1
    record = app_logs.records[-1]
    assert (
        record.getMessage()
        == f"GitHub returned HTTP {upstream_error_response.status_code}"
    )
    assert record.levelno == (
        logging.ERROR if upstream_error_response.status_code >= 500 else logging.WARNING
    )
    assert "octocat" not in record.getMessage()
    assert "Upstream error" not in record.getMessage()


@pytest.mark.mock
def test_preserves_timeout_without_retry(
    github_client_factory, timeout_error, github_requests, app_logs
):
    github_client = github_client_factory(timeout_error)

    with pytest.raises(httpx2.TimeoutException) as caught:
        github_client.list_public_gists("octocat")

    assert caught.value is timeout_error
    assert len(github_requests) == 1
    record = app_logs.records[-1]
    assert (
        record.getMessage() == f"GitHub request failed: {type(timeout_error).__name__}"
    )
    assert record.levelno == logging.ERROR
    assert str(timeout_error) not in record.getMessage()


@pytest.mark.mock
def test_preserves_network_error_without_retry(
    github_client_factory, network_error, github_requests, app_logs
):
    github_client = github_client_factory(network_error)

    with pytest.raises(httpx2.NetworkError) as caught:
        github_client.list_public_gists("octocat")

    assert caught.value is network_error
    assert len(github_requests) == 1
    record = app_logs.records[-1]
    assert (
        record.getMessage() == f"GitHub request failed: {type(network_error).__name__}"
    )
    assert record.levelno == logging.ERROR
    assert str(network_error) not in record.getMessage()
