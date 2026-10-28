import httpx2
import pytest


@pytest.mark.mock
def test_returns_status_200_with_public_gists(
    route_client, mock_github_client, public_gists
):
    response = route_client.get("/v1/alice")

    assert response.status_code == 200
    assert response.json() == public_gists
    mock_github_client.list_public_gists.assert_called_once_with("alice")


@pytest.mark.mock
def test_returns_status_200_with_empty_list(route_client, mock_github_client):
    mock_github_client.list_public_gists.return_value = []

    response = route_client.get("/v1/alice")

    assert response.status_code == 200
    assert response.json() == []
    mock_github_client.list_public_gists.assert_called_once_with("alice")


@pytest.mark.mock
def test_returns_404_for_unknown_path_without_calling_github(
    route_client, mock_github_client, unknown_path
):
    response = route_client.get(unknown_path)

    assert response.status_code == 404
    mock_github_client.list_public_gists.assert_not_called()


@pytest.mark.mock
def test_returns_405_for_unsupported_method_without_calling_github(
    route_client, mock_github_client, unsupported_method
):
    response = route_client.request(unsupported_method, "/v1/alice")

    assert response.status_code == 405
    assert "GET" in response.headers["allow"]
    mock_github_client.list_public_gists.assert_not_called()


@pytest.mark.mock
def test_returns_400_for_invalid_username_without_calling_github(
    route_client, mock_github_client
):
    response = route_client.get("/v1/bad%20user")

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid GitHub username"}
    mock_github_client.list_public_gists.assert_not_called()


@pytest.mark.mock
def test_returns_504_for_timeout_without_exposing_upstream_error(
    route_client, mock_github_client
):
    mock_github_client.list_public_gists.side_effect = httpx2.ReadTimeout(
        "Internal upstream error details"
    )

    response = route_client.get("/v1/alice")

    assert response.status_code == 504
    assert response.json() == {"detail": "GitHub request timed out"}
    assert "Internal upstream error details" not in response.text
    mock_github_client.list_public_gists.assert_called_once_with("alice")


@pytest.mark.mock
def test_returns_503_with_retry_after_for_rate_limit(
    route_client, mock_github_client, upstream_error_factory
):
    mock_github_client.list_public_gists.side_effect = upstream_error_factory(
        429, {"Retry-After": "60"}
    )

    response = route_client.get("/v1/alice")

    assert response.status_code == 503
    assert response.json() == {"detail": "GitHub rate limit exceeded"}
    assert response.headers["retry-after"] == "60"
    mock_github_client.list_public_gists.assert_called_once_with("alice")
