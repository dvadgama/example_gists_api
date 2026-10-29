# Project plan

## Objectives

### Mandatory

- An API server with automated tests to retrieve a user's public Gists
- A Dockerfile to package the app
- Clear instructions so another developer can run and test it on their machine

### Optional

- Health check (implemented)
- Pagination
- Caching
- CI/CD pipeline
- Frontend

Security boundaries and exclusions are defined in the [design](design.md#10-security-and-operation).

## Steps

1. **Set up development.** Create the VS Code Dev Container and pin Python for development and Docker.

2. **Build incrementally.** Write a test for one behaviour, implement it, then repeat.

3. **Check quality.** Run tests and Ruff, review assertions, and aim for at least 85% coverage.

4. **Review security.** Check the implementation against the agreed [security scope](design.md#10-security-and-operation).

5. **Check Docker.** Build the image, start the container, and test the API.

6. **Consider optional features.** Start these after the mandatory work is complete.

## References

- [Original requirements](../README.md#original-readme)
- [Application design](design.md)
