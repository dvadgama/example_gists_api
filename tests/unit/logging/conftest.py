import pytest


@pytest.fixture(
    params=[
        ("DEBUG", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
        ("INFO", ["INFO", "WARNING", "ERROR", "CRITICAL"]),
        ("WARNING", ["WARNING", "ERROR", "CRITICAL"]),
        ("ERROR", ["ERROR", "CRITICAL"]),
        ("CRITICAL", ["CRITICAL"]),
    ],
)
def log_threshold(request):
    return request.param
