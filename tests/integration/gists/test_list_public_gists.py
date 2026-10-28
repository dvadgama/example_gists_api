import pytest


@pytest.mark.mock
def test_returns_public_gists_with_status_200(
    api_client, public_gists, github_requests, settings
):
    response = api_client.get("/v1/octocat")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == public_gists
    assert len(github_requests) == 1
    request = github_requests[0]
    assert request.method == "GET"
    assert str(request.url) == (
        f"{settings.github_base_url.rstrip('/')}/users/octocat/gists"
    )
    assert "authorization" not in request.headers
    assert request.headers["accept"] == "application/vnd.github+json"
    assert request.headers["user-agent"] == "github-api"
    assert request.headers["x-github-api-version"] == "2026-03-10"
    assert request.extensions["timeout"] == {
        "connect": settings.github_timeout_seconds,
        "read": settings.github_timeout_seconds,
        "write": settings.github_timeout_seconds,
        "pool": settings.github_timeout_seconds,
    }
