import httpx2
import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def api_client(github_requests):
    def github_unavailable(request):
        github_requests.append(request)
        raise httpx2.ReadTimeout("Simulated GitHub outage")

    app = create_app(github_transport=httpx2.MockTransport(github_unavailable))
    with TestClient(app) as client:
        yield client
