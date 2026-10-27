FROM mcr.microsoft.com/devcontainers/base:bookworm

COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /uvx /usr/local/bin/

ENV UV_MANAGED_PYTHON=1 \
    UV_PROJECT_ENVIRONMENT=/home/vscode/.venv \
    PATH="/home/vscode/.venv/bin:${PATH}"

USER vscode
WORKDIR /workspaces/github-api

COPY --chown=vscode:vscode pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

CMD ["sleep", "infinity"]
