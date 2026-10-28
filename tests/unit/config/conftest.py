import pytest


@pytest.fixture(autouse=True)
def isolated_configuration(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GITHUB_BASE_URL", raising=False)
    monkeypatch.delenv("GITHUB_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)


@pytest.fixture(
    params=[
        ("DEBUG", "DEBUG"),
        ("INFO", "INFO"),
        ("WARNING", "WARNING"),
        ("ERROR", "ERROR"),
        ("CRITICAL", "CRITICAL"),
        ("info", "INFO"),
        ("  warning  ", "WARNING"),
    ],
)
def valid_log_level(request):
    return request.param


@pytest.fixture(params=["", " ", "TRACE", "WARN", "NOTSET", "20", 20, None, True])
def invalid_log_level(request):
    return request.param


@pytest.fixture(params=["", " ", "TRACE", "NOTSET", "20"])
def invalid_log_level_setting(request):
    return request.param


@pytest.fixture(params=["environment", "dotenv"])
def log_level_source(request):
    return request.param
