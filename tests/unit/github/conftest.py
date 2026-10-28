import httpx
import pytest

from app.github import GitHubClient


@pytest.fixture
def public_gists():
    return [{"id": "123", "description": "Example gist", "public": True}]


@pytest.fixture
def github_requests():
    return []


@pytest.fixture
def github_response(request):
    return getattr(request, "param", None)


@pytest.fixture
def mock_http_client(settings, public_gists, github_requests, github_response):
    def respond(request: httpx.Request) -> httpx.Response:
        github_requests.append(request)
        if isinstance(github_response, Exception):
            raise github_response
        if github_response is not None:
            return github_response
        return httpx.Response(200, json=public_gists)

    transport = httpx.MockTransport(respond)
    with httpx.Client(
        base_url=settings.github_base_url,
        timeout=settings.github_timeout_seconds,
        transport=transport,
    ) as http_client:
        yield http_client


@pytest.fixture
def github_client(mock_http_client):
    return GitHubClient(mock_http_client)
