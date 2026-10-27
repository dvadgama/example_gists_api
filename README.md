# GitHub API

A Python API for listing a GitHub user's public Gists.

Gist requests use `/v1/user/{username}/gists`. This versioned path is an intentional change from the root-level username path in the original requirements. The app will call GitHub anonymously, with no API token configuration. Health and pagination are optional additions.

## Useful reference documents

- [Application design](docs/design.md)
- [Implementation plan](docs/plan.md)
- [Original README](#original-readme)

## Accepted API Requests

| Request | Endpoint | Behaviour |
| --- | --- | --- |
| `GET` | `/v1/user/{username}/gists` | Return the first page of the user's public Gists as a JSON array |
| `GET` | `/v1/user/{username}/gists?page=2&per_page=30` | Return the requested page of public Gists |
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
curl -i 'http://localhost:8080/v1/user/octocat/gists?page=1&per_page=2'
curl -i http://localhost:8080/health
```

## Develop with VS Code (once implemented)

Prerequisites: VS Code, its Dev Containers extension, and Docker.

1. Open the repository in VS Code.
2. Select **Dev Containers: Reopen in Container**.
3. Allow the environment to install the pinned Python version, locked dependencies, and development tools.
4. Start the application from the container terminal:

   ```bash
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
   ```

The Dev Container will forward port `8080` and include debugging, pytest, and Ruff. It will use the same Python version and locked runtime dependencies as the Docker image.

## Tests and code checks (once implemented)

Inside the development environment:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

The tests will make requests to the app and check its responses. They'll use mocked GitHub responses, so they can run offline. Cases will include Gist retrieval, errors, and timeouts, with pagination and health tests added if those features are implemented.

I'll also run the container and use the curl commands above to check the live connection to GitHub.

## Configuration

| Environment variable | Default | Purpose |
| --- | --- | --- |
| `GITHUB_TIMEOUT_SECONDS` | `5` | Positive, finite timeout in seconds for HTTP connection/read/write/pool operations; not a total request deadline |

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
