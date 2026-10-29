# GitHub API

A small HTTP API for listing a GitHub user's public Gists. There are two ways to get started:

- Run the app locally with Docker Compose.
- Use the build script to create an image in CI/CD and deploy it.

## Working on the code?

See the [developer guide](docs/development.md) for setting up development environment.

## Prerequisites
`Docker` and `Docker compose` must be installed and running on the host.

## Run locally

Run the following from the repository root, in a terminal:

```bash
docker compose up
```

This builds the runtime image and starts the API at `http://localhost:8080`.

Try it:

```bash
curl -i http://localhost:8080/health
curl -i http://localhost:8080/v1/octocat
```

View logs or stop the app:

```bash
docker compose logs -f
docker compose down
```

If port `8080` is already in use, choose another host port:

```bash
API_PORT=8081 docker compose up
```

The API is then available at `http://localhost:8081`.

*Note: There is no live reload in this runtime container.*

## Use the API

| Request | Response |
| --- | --- |
| `GET /v1/{username}` | `200` with a JSON array of public Gists, retaining GitHub's Gist fields |
| `GET /health` | `200` with `{"status":"ok"}` |

A successful request with no public Gists returns `200` with `[]`.

Errors return JSON, such as `{"detail":"GitHub user not found"}`:

| Status | Meaning |
| --- | --- |
| `400` | Invalid username |
| `404` | Unknown route, or GitHub reports that the user was not found |
| `405` | Unsupported HTTP method |
| `502` | Other GitHub HTTP/network failure or invalid response |
| `503` | Recognised GitHub rate limit; a valid `Retry-After` header is passed on when available |
| `504` | GitHub request timed out |


## Things to know

1. The API returns only the first page of public Gists. Pagination and caching are not supported.

2. Gist requests depend on GitHub availability and anonymous-access limits. The app does not retry automatically.

3. A successful health check means this app is responding, not that GitHub is available.

## Configuration

Settings are passed to the container at startup.

### Compose

The defaults are enough to start the app. To override them for a Compose run, set environment variables before the command:

```bash
GITHUB_TIMEOUT_SECONDS=10 LOG_LEVEL=WARNING docker compose up
```

Alternatively, edit the `environment` section in `compose.yml` to set values for your local setup.

You can also provide these settings through a local `.env` file. Values supplied in the shell take priority.

| Setting | Default | Purpose |
| --- | --- | --- |
| `GITHUB_BASE_URL` | `https://api.github.com` | Base URL for outgoing GitHub API requests; must be an absolute HTTPS URL |
| `GITHUB_TIMEOUT_SECONDS` | `5` | Finite, positive timeout in seconds for individual connect, read, write, and connection-pool operations; not a total request deadline |
| `LOG_LEVEL` | `INFO` | Minimum application-log severity: `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` |
| `API_PORT` | `8080` | Host port used by Compose, not an application setting |

- Invalid application settings stop startup.
- `.env`, if used, stays local and is excluded from Git and Docker builds.

- `LOG_LEVEL` controls application logs, not Uvicorn's logs.

- After changing settings, run `docker compose up` again. `docker compose restart` does not apply environment changes.


### Docker

For a deployment outside Compose, supply the same application variables through your deployment platform's container environment, or use Docker's `-e` option:

```bash
docker run --rm -p 127.0.0.1:8080:8080 \
  -e GITHUB_TIMEOUT_SECONDS=10 \
  -e LOG_LEVEL=WARNING \
  github-api
```

## Build an image in CI/CD

Use a runner with a POSIX shell and access to a Docker engine. From the checked-out repository root:

```bash
./scripts/build.sh
```

The default image name is `github-api`. Supply an image tag to identify a pipeline build, for example:

```bash
./scripts/build.sh github-api:build-123
```

The script builds the root Dockerfile and returns Docker's exit status, so a failed build fails the pipeline step.

## Container image

- The image uses the Python version pinned in `pyproject.toml`.
- Runtime dependencies are installed from `uv.lock`; development tools are excluded.
- The application runs as a non-root user and listens on `0.0.0.0:8080`.
- The `.env` file is not included in the image.

## Further reading

- [Developer guide](docs/development.md)
- [Application design](docs/design.md)
- [Project plan](docs/plan.md)
- [Original README](#original-readme)

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
