from app.main import health


def test_returns_ok_status():
    assert health() == {"status": "ok"}
