import pytest


@pytest.mark.mock
def test_returns_status_200_without_calling_github(api_client, github_requests):
    response = api_client.get("/health")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"status": "ok"}
    assert github_requests == []


@pytest.mark.mock
def test_remains_healthy_when_github_is_unavailable(api_client, github_requests):
    assert api_client.get("/v1/octocat").status_code == 504
    assert len(github_requests) == 1

    response = api_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert len(github_requests) == 1


@pytest.mark.mock
def test_rejects_post_without_calling_github(api_client, github_requests):
    response = api_client.post("/health")

    assert response.status_code == 405
    assert "GET" in response.headers["allow"]
    assert github_requests == []
