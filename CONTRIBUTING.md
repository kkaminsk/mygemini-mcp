# Contributing

## Branching Model
- Trunk-based development on `main`.
- Short-lived feature branches: `feat/<short-desc>`, `fix/<short-desc>`, `chore/<short-desc>`.
- Rebase or squash-merge PRs to keep history clean.

## Commit Messages (Conventional Commits)
- Format: `<type>(<scope>): <subject>`
- Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`, `build`.
- Examples:
  - `feat(server): add triage routing interface`
  - `fix(mcp): return METHOD_NOT_FOUND for unknown method`

## Pull Requests
- Ensure CI is green: lint (ruff), format (black), type-check (mypy), tests (pytest), pre-commit hooks.
- Add/adjust tests for behavior changes, especially around `mcp_handler`, `security`, and tool registry.

## Coding Standards
- Python 3.12+, async-first with FastAPI.
- Pydantic for schemas and validation.
- Secrets via environment; never commit `.env`.

## Release Process
- Merge to `main` triggers CI. Tag releases using `vX.Y.Z` as needed.
