# Developer guide

This guide is for working on the code.

See the [README](../README.md) for build and run instructions.

## Development environment

### VS Code Dev Container

Requires VS Code, the Dev Containers extension, and Docker.

1. Open the repository in VS Code.
2. Run **Dev Containers: Reopen in Container** from the Command Palette.
3. Wait for dependencies and Git hooks to install.

### Local setup

Install uv on your host, then run first setup environment variables .

```bash
export UV_MANAGED_PYTHON=1                      # Use uv-managed Python
export UV_PROJECT_ENVIRONMENT="$HOME/.venv"     # Project virtual environment
export PATH="$UV_PROJECT_ENVIRONMENT/bin:$PATH" # Add its executables to PATH
```
next, run these commands

```bash
uv sync --locked
uv run --locked pre-commit install
```

Python's version comes from `pyproject.toml`. 

## Run the development server

Start the server with automatic reload:

```bash
uv run --locked uvicorn app.main:app --app-dir src --host 0.0.0.0 --port 8080 --reload
```

Try it from another terminal:

```bash
curl -i http://localhost:8080/health
curl -i http://localhost:8080/v1/octocat
```

If using the Dev Container, forward port `8080` through VS Code's **Ports** panel.

## Local configuration

Copy `.env.example` to `.env`, edit the settings, and restart the server.

See the [README](../README.md#configuration) for available settings.

## Logging

Logging is enabled by default when the server starts. To disable Uvicorn's access logs, add `--no-access-log`:

```bash
uv run --locked uvicorn app.main:app --app-dir src --host 0.0.0.0 --port 8080 --reload --no-access-log
```

See the [logging design](design.md#9-logging) for the events the application records and its privacy choices.

## Find your way around

```text
src/app/
  main.py                Application setup, health, and router registration
  routes.py              Versioned Gist routes and HTTP error translation
  github.py              GitHub requests and response validation
  config.py              Environment settings and validation
  logging.py             Standard logging setup
tests/conftest.py        Shared fixtures
tests/unit/<component>/  Unit tests and component-specific conftest.py fixtures
tests/integration/<feature>/
                         Integration tests and feature-specific conftest.py fixtures
scripts/build.sh         Runtime image build script
.devcontainer/           VS Code development environment
Dockerfile               Runtime image
compose.yml              Local runtime-container setup
```

Imports use `app.*`, not `src.app.*`. Pytest adds `src` to its import path and discovers tests in the root `tests/` directory. VS Code uses the same source and test locations.

The [design](design.md#component-responsibilities) explains why the application is split into these components.

## Run tests and code checks

Commit hooks run Ruff and pytest for Python changes.

```bash
uv run --locked pytest
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pre-commit run --all-files
```

Apply formatting with `uv run --locked ruff format .`.

Check the 85% coverage target:

```bash
uv run --locked pytest --cov=app --cov-branch --cov-report=term-missing --cov-fail-under=85
```

Tests run without calling GitHub. To test one component:

```bash
uv run --locked pytest tests/unit/config
```

The `mock` marker identifies tests that simulate GitHub. The default selection is `not real`, so it includes unmarked tests as well as mocked tests. Any future tests that call live GitHub must use `@pytest.mark.real`.

No live tests have been added yet. Once present, run them explicitly with:

```bash
uv run --locked pytest tests/integration -m real
```

Live checks depend on GitHub availability and anonymous-access limits; keep them out of the default suite.

## Update dependencies

```bash
uv lock --upgrade
uv sync --locked
```

Run the checks and commit the updated `uv.lock`.

## Docker

Run Docker commands from a host terminal. See the [README](../README.md#run-locally) for build and run instructions.

## Local Minikube deployment

The CI workflow starts for:

- Pull requests targeting the `solution` branch.
- Pushes to the `solution` branch.
- Manual `workflow_dispatch` runs.

The lint, test, dependency-audit, and image-check jobs run for all three events. The `app-run` job has `if: github.event_name == 'push'`, so it deploys to local Minikube only after a push to `solution`; it does not deploy for pull requests or manual runs.

On a deployment run, `app-run` builds the image on the self-hosted runner, loads it into the Minikube Docker runtime, and creates a Deployment and a NodePort Service in the `default` namespace.

### Configure the self-hosted runner

The deployment job uses `runs-on: local-runner`. Register the local machine as a repository runner before using the workflow:

1. Open the GitHub repository and go to **Settings → Actions → Runners**.
2. Select **New self-hosted runner**, choose the local operating system and architecture, and run the installation and registration commands shown by GitHub.
3. Assign the custom label `local-runner` to the runner. It can be added in the runner's GitHub settings or during initial registration:

   ```bash
   ./config.sh --url <repository-url> \
     --token <registration-token> \
     --labels local-runner
   ```

4. Start the runner with `./run.sh`, or install and start it as a background service:

   ```bash
   ./svc.sh install
   ./svc.sh start
   ```

Follow GitHub's documentation for [adding a self-hosted runner](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners), [assigning custom labels](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/apply-labels), and [running it as a service](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/configure-the-application?platform=mac).

The runner user must be able to run Docker and `kubectl`. Docker Desktop and Minikube must be running, the kubeconfig must contain the `minikube` context, and the Minikube Docker container must be named `minikube` because the workflow loads the image with `docker exec minikube`.

### Inspect the deployment

Check the deployed resources:

```bash
kubectl --context minikube --namespace default \
  get deployment,pods,service
```

The Service output contains two ports, for example:

```text
PORT(S)
8080:31812/TCP
```

- `8080` is the Service port inside Kubernetes.
- `31812` is an example NodePort allocated from Kubernetes' default `30000-32767` range.
- A NodePort is directly accessible only when the node IP is reachable from the host.

### Access from macOS with the Docker driver

With Minikube's Docker driver on macOS, the node runs inside Docker Desktop's Linux VM. Its IP is not directly routable from macOS, so `http://<minikube-ip>:<node-port>` does not work even though the pod and Service are healthy.

Forward the Service to `localhost:8080`:

```bash
kubectl --context minikube --namespace default \
  port-forward service/github-api 8080:8080
```

Keep that command running, then use the API from another terminal:

```bash
curl -i http://127.0.0.1:8080/health
curl -i http://127.0.0.1:8080/v1/octocat
```

Alternatively, if the Minikube CLI is installed, run the following command and keep its terminal open:

```bash
minikube service github-api --namespace default --url
```

This prints a temporary localhost URL. See Minikube's [accessing applications](https://minikube.sigs.k8s.io/docs/handbook/accessing/) documentation for the Docker-driver networking limitations and other exposure options.

The application does not define a route at `/`; use `/health` or `/v1/{username}`.

