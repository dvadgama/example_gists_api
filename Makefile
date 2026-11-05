.PHONY: test coverage run

test:
	uv run --locked pytest

coverage:
	uv run --locked pytest --cov=app --cov-branch --cov-report=term-missing --cov-fail-under=85

run:
	uv run --locked uvicorn app.main:app --app-dir src --host 0.0.0.0 --port 8080 --reload
