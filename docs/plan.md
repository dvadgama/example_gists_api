# Project plan

I have treated the [original README](../README.md#original-readme) as the requirements document. The project's Gist endpoint will be `/v1/user/{username}/gists`, an intentional change from the original root-level path. No compatibility alias is planned.

## Project Objectives

### Mandatory

- An API server with automated tests to retrieve a user's public Gists
- A Dockerfile to package the app
- Clear instructions so another developer can run and test it on their machine

### Optional

- Health check
- Pagination
- Caching
- CI/CD pipeline
- Frontend

### Out of scope

- Automatic retries when GitHub rate-limits a request
- Incoming API rate limiting
- Caller authentication and authorisation
- HTTPS termination for incoming traffic
- GitHub API token configuration requests to GitHub will be anonymous

## Steps

1. **Set up the project.** Use a VS Code Dev Container for a reusable development environment. Choose the latest stable Python version at setup and pin it for development and the runtime image.

2. **Write tests.** Write tests for each behaviour before implementing it.

3. **Write code.** Implement one behaviour at a time and check that its tests pass.

4. **Check test coverage.** I'll aim for at least 85% coverage and review the assertions as well as the percentage to see what the tests actually verify.

5. **Repeat.** Repeat steps 2–4 until the project's mandatory goals are met.

6. **Run it in Docker.** Build and check an image that listens on port `8080` and runs as a non-root user with minimal privileges. Use the image name `github-api` in the build and run commands.

7. **Optional features.** If time permits, add:

   - `/health` check endpoint
   - Pagination support
   - Caching support
   - A CI/CD pipeline
   - A frontend UI

8. **Security consideration.**

   - In Scope
     - Input validation
     - outbound HTTPS verification
     - safe logging
     - non-root container

   - out of scope
     - Caller authentication and authorisation
     - incoming API rate limiting
     - HTTPS termination
