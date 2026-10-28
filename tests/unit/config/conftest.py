import pytest


@pytest.fixture(autouse=True)
def isolated_configuration(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GITHUB_BASE_URL", raising=False)
    monkeypatch.delenv("GITHUB_TIMEOUT_SECONDS", raising=False)
