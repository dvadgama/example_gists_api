import pytest

from app.config import Settings


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def public_gists():
    return [{"id": "123", "description": "Example gist", "public": True}]


@pytest.fixture
def github_requests():
    return []
