import httpx2
import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def github_transport(public_gists, github_requests):
    def respond(request: httpx2.Request) -> httpx2.Response:
        github_requests.append(request)
        return httpx2.Response(200, json=public_gists)

    return httpx2.MockTransport(respond)


@pytest.fixture
def api_client(github_transport):
    app = create_app(github_transport=github_transport)
    with TestClient(app) as client:
        yield client
