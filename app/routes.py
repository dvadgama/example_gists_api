from email.utils import format_datetime, parsedate_to_datetime
from re import fullmatch

import httpx
from fastapi import APIRouter, HTTPException, Request

from app.github import GitHubClient, InvalidGitHubResponseError

router = APIRouter()


def _valid_retry_after(value: str | None) -> str | None:
    if value is None:
        return None
    if fullmatch(r"[0-9]+", value):
        return value
    try:
        date = parsedate_to_datetime(value)
        if format_datetime(date, usegmt=True) == value:
            return value
    except TypeError, ValueError, OverflowError:
        pass
    return None


def _is_rate_limit(response: httpx.Response, retry_after: str | None) -> bool:
    if response.status_code == 429:
        return True
    if response.status_code != 403:
        return False
    if response.headers.get("x-ratelimit-remaining") == "0" or retry_after is not None:
        return True
    try:
        body = response.json()
    except ValueError:
        return False
    message = body.get("message") if isinstance(body, dict) else None
    return isinstance(message, str) and any(
        phrase in message.lower()
        for phrase in ("api rate limit exceeded", "secondary rate limit")
    )


@router.get("/{username}")
def list_public_gists(username: str, request: Request) -> list[dict[str, object]]:
    if not isinstance(username, str) or not fullmatch(r"[A-Za-z0-9_-]{1,39}", username):
        raise HTTPException(status_code=400, detail="Invalid GitHub username")

    github_client: GitHubClient = request.app.state.github_client
    try:
        return github_client.list_public_gists(username)
    except httpx.TimeoutException as error:
        raise HTTPException(
            status_code=504, detail="GitHub request timed out"
        ) from error
    except httpx.HTTPStatusError as error:
        if error.response.status_code == 404:
            raise HTTPException(
                status_code=404, detail="GitHub user not found"
            ) from error
        retry_after = _valid_retry_after(error.response.headers.get("retry-after"))
        if _is_rate_limit(error.response, retry_after):
            headers = {"Retry-After": retry_after} if retry_after is not None else None
            raise HTTPException(
                status_code=503,
                detail="GitHub rate limit exceeded",
                headers=headers,
            ) from error
        raise HTTPException(status_code=502, detail="GitHub request failed") from error
    except InvalidGitHubResponseError as error:
        raise HTTPException(
            status_code=502, detail="GitHub returned an invalid response"
        ) from error
    except httpx.RequestError as error:
        raise HTTPException(status_code=502, detail="GitHub request failed") from error
