import pytest

from app.config import Settings, _validate_github_timeout_seconds


@pytest.mark.parametrize("value", [0.1, 2.5, 5, 30.0, "2.5"])
def test_accepts_valid_timeout(value):
    assert _validate_github_timeout_seconds(value) is None


@pytest.mark.parametrize(
    "value",
    [
        0,
        -1,
        float("nan"),
        float("inf"),
        float("-inf"),
        "invalid",
        "",
        None,
    ],
)
def test_rejects_invalid_timeout_value(value):
    with pytest.raises(
        ValueError, match="GITHUB_TIMEOUT_SECONDS must be a finite, positive number"
    ):
        _validate_github_timeout_seconds(value)


@pytest.mark.parametrize("source", ["environment", "dotenv"])
@pytest.mark.parametrize("value", ["0", "-1", "nan", "inf", "-inf", "invalid", ""])
def test_rejects_invalid_timeout(source, value, monkeypatch, tmp_path):
    if source == "environment":
        monkeypatch.setenv("GITHUB_TIMEOUT_SECONDS", value)
    else:
        (tmp_path / ".env").write_text(
            f"GITHUB_TIMEOUT_SECONDS={value}\n", encoding="utf-8"
        )

    with pytest.raises(
        ValueError, match="GITHUB_TIMEOUT_SECONDS must be a finite, positive number"
    ):
        Settings()
