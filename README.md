# GitHub API

A Python API for listing a GitHub user's public Gists.

Gist requests use `/v1/{username}`. This versioned path is an intentional change from the root-level username path in the original requirements. The app will call GitHub anonymously, with no API token configuration. Health and pagination are optional additions.

## Useful reference documents

- [Application design](docs/design.md)
- [Implementation plan](docs/plan.md)
- [Original README](#original-readme)

## Accepted API Requests

| Request | Endpoint | Behaviour |
| --- | --- | --- |
| `GET` | `/v1/{username}` | Return the first page of the user's public Gists as a JSON array |
| `GET` | `/v1/{username}?page=2&per_page=30` | Return the requested page of public Gists |
| `GET` | `/health` | Return `200` with `{"status":"ok"}` |

## Run with Docker

Prerequisite: Docker with a running container engine. Python does not need to be installed on the host for this workflow.

Run these commands from the repository root once implementation is complete:

```bash
docker build -t github-api .
docker run --rm -p 8080:8080 github-api
```

In another terminal, request Gists and include the response headers to inspect pagination:

```bash
curl -i 'http://localhost:8080/v1/octocat?page=1&per_page=2'
curl -i http://localhost:8080/health
```

## Develop with VS Code

Prerequisites: VS Code, its Dev Containers extension, and Docker.

1. Open the repository in VS Code.
2. Select **Dev Containers: Reopen in Container**.
3. Wait for the container to build. uv installs the Python version specified by `requires-python` in `pyproject.toml`.
4. Check the tools in the container terminal:

   ```bash
   uv --version
   python --version
   ```

The setup includes Python, uv, pytest, pytest-cov, Ruff, and pre-commit. VS Code has Python test discovery and Ruff formatting enabled. The Dev Container installs the locked development dependencies and Git commit hooks after creation. The GitHub client and configuration have unit tests; the HTTP server and runtime Dockerfile will follow later.

The Python version is defined only in `pyproject.toml`; there is no `.python-version` file. After changing it, use **Dev Containers: Rebuild Container**. The virtual environment lives at `/home/vscode/.venv`, outside the mounted source folder, and the container runs as the non-root `vscode` user.

To build and check the development image without opening VS Code, run these commands from the repository root:

```bash
docker build -f .devcontainer/Dockerfile -t github-api-dev .
docker run --rm github-api-dev uv --version
docker run --rm github-api-dev python --version
```

## Tests and code checks

Inside the development environment:

```bash
uv run --locked pre-commit run --all-files
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest
```

The commit hooks check linting and formatting, then run the default test suite when Python files are staged. They report problems without automatically modifying files. Test failures block commits. To apply formatting, run `uv run --locked ruff format .`.

The hooks are installed for the container environment, so make commits from VS Code while connected to the Dev Container or from its terminal. If setting up another uv environment, install its dependencies and hooks there:

```bash
uv sync --locked
uv run --locked pre-commit install
```

Check the project's 85% coverage target with:

```bash
uv run --locked pytest --cov=app --cov-branch --cov-report=term-missing --cov-fail-under=85
```

The current tests cover configuration and a successful GitHub client request. They use temporary configuration files and mocked GitHub responses, so they can run offline. Unit tests live under `tests/unit/<component>/test_<function>.py`. Shared fixtures belong in `conftest.py`: general settings at the test root, config isolation under `unit/config`, and mocked HTTP clients under `unit/github`.

Integration tests will live under `tests/integration/<feature>`. Tests that call live GitHub must be marked `real`; they are excluded by default, including in pre-commit. No integration tests have been added yet.

Run one component, one function's tests, or (once added) the live integration tests:

```bash
uv run --locked pytest tests/unit/config
uv run --locked pytest tests/unit/github/test_list_public_gists.py
uv run --locked pytest tests/integration -m real
```

I'll also run the container and use the curl commands above to check the live connection to GitHub.

## Configuration

For local development, run commands from the repository root. If you do not already have a `.env` file, create one from the example:

```bash
cp .env.example .env
uv sync --locked
```

Edit `.env` to change the configuration:

```dotenv
GITHUB_BASE_URL=https://api.github.com
GITHUB_TIMEOUT_SECONDS=5
```

`Settings()` reads `.env` from the current working directory. Environment variables take priority over `.env`, and built-in defaults are used when neither supplies a value. The file is optional. Restart the application after changing settings.

Each configuration getter validates its value before returning it. Use `Settings()` to load validated configuration; supplying field values directly to the dataclass bypasses those getters and their validation.

Both mocked and live clients use the same settings; mocked tests replace the HTTP transport, not the URL. Configuration tests use their own temporary directory so your local `.env` cannot affect them.

| Environment variable | Default | Purpose |
| --- | --- | --- |
| `GITHUB_BASE_URL` | `https://api.github.com` | Base URL for outgoing GitHub API requests |
| `GITHUB_TIMEOUT_SECONDS` | `5` | Positive, finite timeout in seconds for connection, read, write, and connection-pool operations |

The base URL must be an absolute HTTPS URL with a valid hostname and, if supplied, a port from `1` to `65535`. Credentials, query strings, fragments, whitespace, and backslashes are rejected. Custom HTTPS hosts and path prefixes are allowed; validation does not contact the server or check whether it is GitHub.

The timeout accepts decimals, such as `2.5`. It applies to individual network operations, not the total duration of a request. Empty values, non-numeric values, zero, negative numbers, and infinity are rejected when settings are loaded.

Commit `.env.example`, but keep `.env` local. `.env` and other `.env.*` files are already excluded from Git and Docker builds, with `.env.example` allowed in Git. No GitHub API token is needed.

Once the runtime image is implemented, pass the same file to Docker rather than copying it into the image:

```bash
docker run --rm --env-file .env -p 8080:8080 github-api
```

The app will listen on `0.0.0.0:8080` and run as a non-root user. Settings will come from the environment and logs will go to standard output, without Gist contents.

Gist requests depend on GitHub being available and may hit its rate limits. Each request will fetch one page without caching initially. Results can also change between page requests as Gists are added or updated.

## Original README

The original project requirements follow unchanged.

## :warning: Please read these instructions carefully and entirely first
* Clone this repository to your local machine.
* Use your IDE of choice to complete the assignment.
* When you have completed the assignment, you need to  push your code to this repository and [mark the assignment as completed by clicking here](https://app.snapcode.review/submission_links/a4ef34f6-a9a7-403e-a7f8-6e9dd17836db).
* Once you mark it as completed, your access to this repository will be revoked. Please make sure that you have completed the assignment and pushed all code from your local machine to this repository before you click the link.

## Operability Take-Home Exercise

Welcome to the start of our recruitment process for Operability Engineers. It was great to speak to you regarding an opportunity to join the Equal Experts network!

Please write code to deliver a solution to the problems outlined below.

We appreciate that your time is valuable and do not expect this exercise to **take more than 90 minutes**. If you think this exercise will take longer than that, I **strongly** encourage you to please get in touch to ask any clarifying questions.

### Submission guidelines
**Do**
- Provide a README file in text or markdown format that documents a concise way to set up and run the provided solution.
- Take the time to read any applicable API or service docs, it may save you significant effort.
- Make your solution simple and clear. We aren't looking for overly complex ways to solve the problem since in our experience, simple and clear solutions to problems are generally the most maintainable and extensible solutions.

**Don't**

Expect the reviewer to dedicate a machine to review the test by:

- Installing software globally that may conflict with system software
- Requiring changes to system-wide configurations
- Providing overly complex solutions that need to spin up a ton of unneeded supporting dependencies. We aspire to keep our dev experiences as simple as possible (but no simpler)!
- Include identifying information in your submission. We are endeavouring to make our review process anonymous to reduce bias.

### Exercise
If you have any questions on the below exercise, please do get in touch and we’ll answer as soon as possible.

#### Build an API, test it, and package it into a container
- Build a simple HTTP web server API in any general-purpose programming language[^1] that interacts with the GitHub API and responds to requests on `/<USER>` with a list of the user’s publicly available Gists[^2].
- Create an automated test to validate that your web server API works. An example user to use as test data is `octocat`.
- Package the web server API into a docker container that listens for requests on port `8080`. You do not need to publish the resulting container image in any container registry, but we are expecting the Dockerfile in the submission.
- The solution may optionally provide other functionality (e.g. pagination, caching) but the above **must** be implemented.

Best of luck,  
Equal Experts
__________________________________________
[^1]: For example Go, Python or Ruby but not Bash or Powershell.  
[^2]: https://docs.github.com/en/rest/gists/gists?apiVersion=2022-11-28
