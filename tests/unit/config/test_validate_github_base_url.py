import pytest

from app.config import Settings, _validate_github_base_url


@pytest.mark.parametrize(
    "value",
    [
        "https://api.github.com",
        "https://github.example.test:8443/api/v3",
        "https://[::1]:8443",
    ],
)
def test_accepts_valid_https_base_url(value):
    assert _validate_github_base_url(value) is None


@pytest.mark.parametrize("source", ["environment", "dotenv", "validator"])
@pytest.mark.parametrize(
    "value",
    [
        "",
        "http://api.github.com",
        "ftp://api.github.com",
        "api.github.com",
        "https://",
        "https:///gists",
        "https://bad host.example",
        "https://-bad.example",
        "https://bad_.example",
        "https://api.github.com:invalid",
        "https://api.github.com:70000",
        "https://api.github.com:0",
        "https://api.github.com:",
        "https://[invalid]",
        "https://user:password@api.github.com",
        "https://@api.github.com",
        "https://api.github.com?token=secret",
        "https://api.github.com#fragment",
        "https://api.github.com?",
        "https://api.github.com#",
        " https://api.github.com",
        "https://api.github.com/\\gists",
    ],
)
def test_rejects_invalid_base_url(source, value, monkeypatch, tmp_path):
    if source == "environment":
        monkeypatch.setenv("GITHUB_BASE_URL", value)
    elif source == "dotenv":
        (tmp_path / ".env").write_text(f"GITHUB_BASE_URL='{value}'\n", encoding="utf-8")

    with pytest.raises(ValueError, match="GITHUB_BASE_URL must be"):
        if source == "validator":
            _validate_github_base_url(value)
        else:
            Settings()
