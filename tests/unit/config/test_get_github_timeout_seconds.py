from app.config import Settings


def test_defaults_to_five_second_timeout():
    settings = Settings()

    assert settings.github_timeout_seconds == 5.0


def test_reads_timeout_from_environment(monkeypatch):
    monkeypatch.setenv("GITHUB_TIMEOUT_SECONDS", "2.5")

    settings = Settings()

    assert settings.github_timeout_seconds == 2.5


def test_reads_timeout_from_dotenv(tmp_path):
    (tmp_path / ".env").write_text("GITHUB_TIMEOUT_SECONDS=3.5\n", encoding="utf-8")

    settings = Settings()

    assert settings.github_timeout_seconds == 3.5


def test_timeout_environment_takes_priority_over_dotenv(monkeypatch, tmp_path):
    (tmp_path / ".env").write_text("GITHUB_TIMEOUT_SECONDS=3.5\n", encoding="utf-8")
    monkeypatch.setenv("GITHUB_TIMEOUT_SECONDS", "2.5")

    settings = Settings()

    assert settings.github_timeout_seconds == 2.5
