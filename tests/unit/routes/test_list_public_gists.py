import httpx
import pytest
from fastapi import HTTPException

from app.routes import list_public_gists


@pytest.mark.mock
def test_returns_public_gists_from_client(
    route_request, mock_github_client, public_gists
):
    result = list_public_gists(username="alice", request=route_request)

    assert result == public_gists
    mock_github_client.list_public_gists.assert_called_once_with("alice")


@pytest.mark.mock
def test_returns_empty_list_when_client_has_no_public_gists(
    route_request, mock_github_client
):
    mock_github_client.list_public_gists.return_value = []

    result = list_public_gists(username="bob", request=route_request)

    assert result == []
    mock_github_client.list_public_gists.assert_called_once_with("bob")


@pytest.mark.mock
def test_rejects_invalid_username_without_calling_github(
    route_request, mock_github_client, invalid_username
):
    with pytest.raises(HTTPException) as caught:
        list_public_gists(username=invalid_username, request=route_request)

    assert caught.value.status_code == 400
    mock_github_client.list_public_gists.assert_not_called()


@pytest.mark.mock
def test_passes_valid_username_to_github_unchanged(
    route_request, mock_github_client, public_gists, valid_username
):
    result = list_public_gists(username=valid_username, request=route_request)

    assert result == public_gists
    mock_github_client.list_public_gists.assert_called_once_with(valid_username)


@pytest.mark.mock
def test_maps_github_user_not_found_to_404(
    route_request, mock_github_client, upstream_error_factory
):
    mock_github_client.list_public_gists.side_effect = upstream_error_factory(404)

    with pytest.raises(HTTPException) as caught:
        list_public_gists(username="alice", request=route_request)

    assert caught.value.status_code == 404
    mock_github_client.list_public_gists.assert_called_once_with("alice")


@pytest.mark.mock
def test_maps_timeout_to_504_without_retry(
    route_request, mock_github_client, timeout_error
):
    mock_github_client.list_public_gists.side_effect = timeout_error

    with pytest.raises(HTTPException) as caught:
        list_public_gists(username="alice", request=route_request)

    assert caught.value.status_code == 504
    mock_github_client.list_public_gists.assert_called_once_with("alice")


@pytest.mark.mock
def test_maps_invalid_response_to_502(
    route_request, mock_github_client, invalid_response_error
):
    mock_github_client.list_public_gists.side_effect = invalid_response_error

    with pytest.raises(HTTPException) as caught:
        list_public_gists(username="alice", request=route_request)

    assert caught.value.status_code == 502
    mock_github_client.list_public_gists.assert_called_once_with("alice")


@pytest.mark.mock
def test_maps_transport_error_to_502_without_retry(
    route_request, mock_github_client, transport_error
):
    mock_github_client.list_public_gists.side_effect = transport_error

    with pytest.raises(HTTPException) as caught:
        list_public_gists(username="alice", request=route_request)

    assert caught.value.status_code == 502
    mock_github_client.list_public_gists.assert_called_once_with("alice")


@pytest.mark.mock
def test_maps_other_upstream_http_errors_to_502(
    route_request, mock_github_client, non_rate_limit_error
):
    mock_github_client.list_public_gists.side_effect = non_rate_limit_error

    with pytest.raises(HTTPException) as caught:
        list_public_gists(username="alice", request=route_request)

    assert caught.value.status_code == 502
    mock_github_client.list_public_gists.assert_called_once_with("alice")


@pytest.mark.mock
def test_maps_recognised_github_rate_limit_to_503(
    route_request, mock_github_client, rate_limit_error
):
    mock_github_client.list_public_gists.side_effect = rate_limit_error

    with pytest.raises(HTTPException) as caught:
        list_public_gists(username="alice", request=route_request)

    assert caught.value.status_code == 503
    mock_github_client.list_public_gists.assert_called_once_with("alice")


@pytest.mark.mock
def test_does_not_treat_unrecognised_forbidden_response_as_rate_limit(
    route_request, mock_github_client, non_rate_limit_forbidden_error
):
    mock_github_client.list_public_gists.side_effect = non_rate_limit_forbidden_error

    with pytest.raises(HTTPException) as caught:
        list_public_gists(username="alice", request=route_request)

    assert caught.value.status_code == 502
    mock_github_client.list_public_gists.assert_called_once_with("alice")


@pytest.mark.mock
def test_preserves_valid_retry_after_for_rate_limit(
    route_request, mock_github_client, upstream_error_factory, valid_retry_after
):
    mock_github_client.list_public_gists.side_effect = upstream_error_factory(
        429, {"Retry-After": valid_retry_after}
    )

    with pytest.raises(HTTPException) as caught:
        list_public_gists(username="alice", request=route_request)

    assert caught.value.status_code == 503
    assert (
        httpx.Headers(caught.value.headers or {}).get("retry-after")
        == valid_retry_after
    )
    mock_github_client.list_public_gists.assert_called_once_with("alice")


@pytest.mark.mock
def test_does_not_forward_invalid_retry_after(
    route_request, mock_github_client, upstream_error_factory, invalid_retry_after
):
    mock_github_client.list_public_gists.side_effect = upstream_error_factory(
        429, {"Retry-After": invalid_retry_after}
    )

    with pytest.raises(HTTPException) as caught:
        list_public_gists(username="alice", request=route_request)

    assert caught.value.status_code == 503
    assert "retry-after" not in httpx.Headers(caught.value.headers or {})
    mock_github_client.list_public_gists.assert_called_once_with("alice")


@pytest.mark.mock
def test_does_not_forward_retry_after_for_other_upstream_errors(
    route_request, mock_github_client, upstream_error_factory
):
    mock_github_client.list_public_gists.side_effect = upstream_error_factory(
        500, {"Retry-After": "60"}
    )

    with pytest.raises(HTTPException) as caught:
        list_public_gists(username="alice", request=route_request)

    assert caught.value.status_code == 502
    assert "retry-after" not in httpx.Headers(caught.value.headers or {})
    mock_github_client.list_public_gists.assert_called_once_with("alice")
