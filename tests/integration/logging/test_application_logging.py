import httpx2
import pytest
from fastapi.testclient import TestClient


@pytest.mark.mock
def test_logs_startup_and_shutdown_without_a_github_request(
    logging_app_factory, app_logs
):
    app = logging_app_factory(AssertionError("GitHub should not be called"))

    with TestClient(app):
        assert [record.getMessage() for record in app_logs.records] == [
            "Application started"
        ]

    assert [record.getMessage() for record in app_logs.records] == [
        "Application started",
        "Application stopping",
    ]


@pytest.mark.mock
def test_success_does_not_log_request_or_gist_details(logging_app_factory, capsys):
    gists = [{"description": "private-gist-description"}]
    app = logging_app_factory(httpx2.Response(200, json=gists))

    with TestClient(app) as client:
        response = client.get(
            "/v1/private-user?secret=private-query",
            headers={"Authorization": "Bearer private-token"},
        )

    assert response.status_code == 200
    assert response.json() == gists
    output = capsys.readouterr().out
    assert len(output.splitlines()) == 2
    for value in (
        "private-user",
        "private-query",
        "private-token",
        "private-gist-description",
    ):
        assert value not in output


@pytest.mark.mock
def test_logs_safe_github_failure_without_changing_response(
    logging_app_factory, capsys
):
    app = logging_app_factory(httpx2.ReadTimeout("private-error-details"))

    with TestClient(app) as client:
        response = client.get("/v1/private-user?secret=private-query")

    assert response.status_code == 504
    assert response.json() == {"detail": "GitHub request timed out"}
    output = capsys.readouterr().out
    assert "ERROR app.github: GitHub request failed: ReadTimeout" in output
    assert "private-error-details" not in output
    assert "private-user" not in output
    assert "private-query" not in output
    assert "Traceback" not in output


@pytest.mark.mock
def test_uses_log_level_from_settings(logging_app_factory, monkeypatch, capsys):
    monkeypatch.setenv("LOG_LEVEL", "warning")
    app = logging_app_factory(httpx2.Response(404, text="private-upstream-body"))

    with TestClient(app) as client:
        assert client.get("/v1/alice").status_code == 404

    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 1
    assert "WARNING app.github: GitHub returned HTTP 404" in lines[0]
    assert "private-upstream-body" not in lines[0]


@pytest.mark.mock
def test_invalid_log_level_stops_startup(logging_app_factory, monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "TRACE")
    app = logging_app_factory(AssertionError("GitHub should not be called"))

    with pytest.raises(ValueError, match="LOG_LEVEL must be one of"):
        with TestClient(app):
            pytest.fail("Application should not start with an invalid log level")
