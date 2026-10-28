import httpx2
import pytest

from app.main import create_app


@pytest.fixture(autouse=True)
def default_log_level(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "INFO")


@pytest.fixture
def logging_app_factory():
    def create_logging_app(response_or_error):
        def respond(request):
            if isinstance(response_or_error, Exception):
                raise response_or_error
            return response_or_error

        return create_app(github_transport=httpx2.MockTransport(respond))

    return create_logging_app
