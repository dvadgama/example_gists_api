from app.config import Settings


def test_defaults_to_github_base_url():
    settings = Settings()

    assert settings.github_base_url == "https://api.github.com"


def test_reads_github_base_url_from_environment(monkeypatch):
    monkeypatch.setenv("GITHUB_BASE_URL", "https://github.example.test")

    settings = Settings()

    assert settings.github_base_url == "https://github.example.test"


def test_reads_github_base_url_from_dotenv(tmp_path):
    (tmp_path / ".env").write_text(
        "GITHUB_BASE_URL=https://github.example.test\n", encoding="utf-8"
    )

    settings = Settings()

    assert settings.github_base_url == "https://github.example.test"


def test_environment_takes_priority_over_dotenv(monkeypatch, tmp_path):
    (tmp_path / ".env").write_text(
        "GITHUB_BASE_URL=https://file.example.test\n", encoding="utf-8"
    )
    monkeypatch.setenv("GITHUB_BASE_URL", "https://environment.example.test")

    settings = Settings()

    assert settings.github_base_url == "https://environment.example.test"
