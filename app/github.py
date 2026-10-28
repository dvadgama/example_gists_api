from urllib.parse import quote

import httpx2


class InvalidGitHubResponseError(Exception):
    """GitHub returned invalid JSON or an unexpected Gist list."""


class GitHubClient:
    def __init__(self, http_client: httpx2.Client):
        self._http_client = http_client

    def list_public_gists(self, username: str) -> list[dict[str, object]]:
        encoded_username = quote(username, safe="")
        response = self._http_client.get(f"/users/{encoded_username}/gists")
        response.raise_for_status()
        try:
            gists = response.json()
        except ValueError as error:
            raise InvalidGitHubResponseError("GitHub returned invalid JSON") from error

        if not isinstance(gists, list) or any(
            not isinstance(gist, dict) for gist in gists
        ):
            raise InvalidGitHubResponseError("GitHub returned an invalid Gist list")
        return gists
