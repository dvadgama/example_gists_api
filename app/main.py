import logging
from contextlib import asynccontextmanager

import httpx2
from fastapi import FastAPI

from app.config import Settings
from app.github import GitHubClient
from app.logging import configure_logging
from app.routes import router

logger = logging.getLogger(__name__)


def create_app(*, github_transport: httpx2.BaseTransport | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        settings = Settings()
        configure_logging(settings.log_level)
        with httpx2.Client(
            base_url=settings.github_base_url,
            timeout=settings.github_timeout_seconds,
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2026-03-10",
                "User-Agent": "github-api",
            },
            transport=github_transport,
        ) as http_client:
            application.state.github_client = GitHubClient(http_client)
            logger.info("Application started")
            try:
                yield
            finally:
                logger.info("Application stopping")

    application = FastAPI(title="GitHub API", lifespan=lifespan)
    application.include_router(router, prefix="/v1")
    return application


app = create_app()
