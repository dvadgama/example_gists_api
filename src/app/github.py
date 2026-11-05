import logging
from urllib.parse import quote

import httpx2

logger = logging.getLogger(__name__)


class InvalidGitHubResponseError(Exception):
    """GitHub returned invalid JSON or an unexpected Gist list."""


class GitHubClient:
    def __init__(self, http_client: httpx2.Client):
        self._http_client = http_client

    def list_public_gists(self, username: str) -> list[dict[str, object]]:
        encoded_username = quote(
            username, safe=""
        )  # Ensures that charcters like / are encoded as name rather than url path
        # Makes url secure
        try:
            response = self._http_client.get(f"/users/{encoded_username}/gists")
            response.raise_for_status()
        except httpx2.HTTPStatusError as error:  # Unsuccessful HTTP response
            status = error.response.status_code
            level = logging.ERROR if status >= 500 else logging.WARNING
            logger.log(level, "GitHub returned HTTP %s", status)
            raise
        except httpx2.RequestError as error:  # This is to capture request/network error for e.g. 404 / 403 /429 etc
            logger.error("GitHub request failed: %s", type(error).__name__)
            raise
        try:
            gists = response.json()
        except ValueError as error:
            logger.error("GitHub returned invalid JSON")
            raise InvalidGitHubResponseError("GitHub returned invalid JSON") from error

        if not isinstance(gists, list) or any(
            not isinstance(gist, dict) for gist in gists
        ):
            logger.error("GitHub returned an invalid Gist list")
            raise InvalidGitHubResponseError("GitHub returned an invalid Gist list")
        return gists
