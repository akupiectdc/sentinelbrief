# GitHub Actions

GitHub Actions is the primary (and only) CI system for this repository. There
are no Azure DevOps pipelines.

## Workflow

`.github/workflows/ci.yml` runs on pushes and pull requests. It has two
independent jobs.

### Python job (`python-ai-service`)

1. Check out the repository.
2. Install [uv](https://docs.astral.sh/uv/) via `astral-sh/setup-uv`.
3. `uv sync` to install dependencies (including dev tools).
4. `uv run ruff check .` for linting.
5. `uv run pytest` for unit tests.

### .NET job (`dotnet-web-api`)

1. Check out the repository.
2. Set up the .NET 8 SDK.
3. `dotnet restore`.
4. `dotnet build --no-restore`.
5. `dotnet test --no-build`.

## CI constraints

CI must **not** require:

* secrets
* Ollama
* Qdrant
* external LLM APIs
* cloud provider credentials

Unit tests use fakes/mocks, so the pipeline is fully self-contained and
deterministic. Integration tests that need real Ollama or Qdrant will be added
later behind a separate, opt-in marker and will not run in the default CI.

## Running the same checks locally

```bash
# Python
cd src/ai-service
uv sync
uv run ruff check .
uv run pytest

# .NET
cd src/web-api
dotnet restore
dotnet build
dotnet test
```
