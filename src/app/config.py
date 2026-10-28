from dataclasses import dataclass, field
from ipaddress import IPv6Address
from math import isfinite
from os import getenv
from re import fullmatch
from urllib.parse import urlsplit

from dotenv import dotenv_values


def _get_github_base_url() -> str:
    file_settings = dotenv_values(".env")
    default_url = file_settings.get("GITHUB_BASE_URL", "https://api.github.com") or ""
    base_url = getenv("GITHUB_BASE_URL", default_url)
    _validate_github_base_url(base_url)
    return base_url


def _validate_github_base_url(value: str) -> None:
    error_message = "GITHUB_BASE_URL must be an absolute HTTPS URL with a valid host and port, without credentials, query strings or fragments"
    try:
        # Any of this condition will raise value error
        if (
            not isinstance(value, str)  # check if it is string
            or "\\" in value  # check for possible directory traversal attempt
            or any(
                char.isspace() or ord(char) < 32 or ord(char) == 127
                for char in value  # if there is a space or invisisble control char
            )
        ):
            raise ValueError(error_message)

        url = urlsplit(value)
        host = url.hostname
        if not host:
            raise ValueError(error_message)
        if ":" in host or url.netloc.startswith("["):
            IPv6Address(host)
        else:
            # Converts international domain names into ascii
            ascii_host = host.encode("idna").decode("ascii").removesuffix(".")
            if len(ascii_host) > 253 or any(
                # regex checks for label to
                # - start with charcter or number
                # - middle part can have char , nunber or hyphe, max length upto 61 char
                # - ends with character or number
                not fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label)
                for label in ascii_host.split(".")
            ):
                raise ValueError(error_message)

        if (
            url.scheme != "https"
            or url.username is not None
            or url.password is not None
            or url.port == 0
            or url.netloc.endswith(":")  # ensures url does not end with ':'
            or "?" in value
            or "#" in value
        ):
            raise ValueError(error_message)
    except (ValueError, UnicodeError) as error:
        raise ValueError(error_message) from error


def _get_github_timeout_seconds() -> float:
    file_settings = dotenv_values(".env")
    default_timeout = file_settings.get("GITHUB_TIMEOUT_SECONDS", "5") or ""
    time_out = getenv("GITHUB_TIMEOUT_SECONDS", default_timeout)

    _validate_github_timeout_seconds(time_out)

    return float(time_out)


def _validate_github_timeout_seconds(value: str) -> None:
    error_message = "GITHUB_TIMEOUT_SECONDS must be a finite, positive number"

    try:
        timeout = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(error_message) from error
    if not isfinite(timeout) or timeout <= 0:
        raise ValueError(error_message)


def _get_log_level() -> str:
    file_settings = dotenv_values(".env")
    default_level = file_settings.get("LOG_LEVEL", "INFO") or ""
    log_level = getenv("LOG_LEVEL", default_level)
    _validate_log_level(log_level)
    return log_level.strip().upper()


def _validate_log_level(value: str) -> None:
    if not isinstance(value, str) or value.strip().upper() not in (
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ):
        raise ValueError(
            "LOG_LEVEL must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL"
        )


@dataclass(frozen=True)
class Settings:
    github_base_url: str = field(default_factory=_get_github_base_url)
    github_timeout_seconds: float = field(default_factory=_get_github_timeout_seconds)
    log_level: str = field(default_factory=_get_log_level)
