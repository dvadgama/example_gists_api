import logging

import pytest

from app.config import Settings


@pytest.fixture(autouse=True)
def restore_app_logging():
    logger = logging.getLogger("app")
    previous_handlers = logger.handlers.copy()
    previous_level = logger.level
    previous_propagate = logger.propagate

    yield

    for handler in logger.handlers.copy():
        if handler not in previous_handlers:
            logger.removeHandler(handler)
            handler.close()
    logger.setLevel(previous_level)
    logger.propagate = previous_propagate


@pytest.fixture
def app_logs(caplog):
    logger = logging.getLogger("app")
    caplog.set_level(logging.INFO, logger="app")
    logger.addHandler(caplog.handler)
    logger.propagate = False
    yield caplog
    logger.removeHandler(caplog.handler)


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def public_gists():
    return [{"id": "123", "description": "Example gist", "public": True}]


@pytest.fixture
def github_requests():
    return []
