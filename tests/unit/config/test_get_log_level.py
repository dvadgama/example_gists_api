from app.config import Settings


def test_defaults_to_info():
    assert Settings().log_level == "INFO"


def test_reads_log_level_from_environment(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    assert Settings().log_level == "DEBUG"


def test_reads_log_level_from_dotenv(tmp_path):
    (tmp_path / ".env").write_text("LOG_LEVEL=ERROR\n", encoding="utf-8")

    assert Settings().log_level == "ERROR"


def test_environment_takes_priority_over_invalid_dotenv_value(monkeypatch, tmp_path):
    (tmp_path / ".env").write_text("LOG_LEVEL=TRACE\n", encoding="utf-8")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")

    assert Settings().log_level == "WARNING"


def test_defaults_when_dotenv_does_not_include_log_level(tmp_path):
    (tmp_path / ".env").write_text("GITHUB_TIMEOUT_SECONDS=5\n", encoding="utf-8")

    assert Settings().log_level == "INFO"


def test_normalises_configured_log_level(
    valid_log_level, log_level_source, monkeypatch, tmp_path
):
    value, expected = valid_log_level
    if log_level_source == "environment":
        monkeypatch.setenv("LOG_LEVEL", value)
    else:
        (tmp_path / ".env").write_text(f'LOG_LEVEL="{value}"\n', encoding="utf-8")

    assert Settings().log_level == expected
