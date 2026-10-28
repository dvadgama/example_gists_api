import pytest

from app.config import Settings, _validate_log_level


def test_accepts_supported_log_level(valid_log_level):
    value, _ = valid_log_level

    assert _validate_log_level(value) is None


def test_rejects_invalid_log_level(invalid_log_level):
    with pytest.raises(
        ValueError,
        match="LOG_LEVEL must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL",
    ):
        _validate_log_level(invalid_log_level)


def test_rejects_invalid_setting(
    invalid_log_level_setting, log_level_source, monkeypatch, tmp_path
):
    if log_level_source == "environment":
        monkeypatch.setenv("LOG_LEVEL", invalid_log_level_setting)
    else:
        (tmp_path / ".env").write_text(
            f'LOG_LEVEL="{invalid_log_level_setting}"\n', encoding="utf-8"
        )

    with pytest.raises(
        ValueError,
        match="LOG_LEVEL must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL",
    ):
        Settings()


def test_rejects_dotenv_key_without_a_value(tmp_path):
    (tmp_path / ".env").write_text("LOG_LEVEL\n", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="LOG_LEVEL must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL",
    ):
        Settings()
