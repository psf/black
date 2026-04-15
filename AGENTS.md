<!-- crag:auto-start -->
# AGENTS.md

> Generated from governance.md by crag. Regenerate: `crag compile --target agents-md`

## Project: black


## Quality Gates

All changes must pass these checks before commit:

### Lint
1. `flake8`
2. `mypy .`
3. `black --check .`

### Test
1. `tox run`

### Build
1. `python -m build`

### Ci (inferred from workflow)
1. `docker buildx imagetools create $TAGS $(printf "$REGISTRY@sha256:%s " *)`
2. `docker buildx imagetools inspect $REGISTRY:latest`
3. `python -m hatch build`
4. `python -m black --check .`

## Coding Standards

- Stack: python, docker
- Follow project commit conventions

## Architecture

- Type: monolith

## Key Directories

- `.github/` — CI/CD
- `docs/` — documentation
- `scripts/` — tooling
- `src/` — source
- `tests/` — tests

## Testing

- Framework: pytest
- Layout: flat
- Naming: test_*.py

## Code Style

- Formatter: prettier

## Anti-Patterns

Do not:
- Do not catch bare `Exception` — catch specific exceptions
- Do not use mutable default arguments (e.g., `def f(x=[])`)
- Do not use `import *` — use explicit imports
- Do not use `latest` tag in FROM — pin to a specific version
- Do not run containers as root — use a non-root USER

## Security

- No hardcoded secrets — grep for sk_live, AKIA, password= before commit

## Workflow

1. Read `governance.md` at the start of every session — it is the single source of truth.
2. Run all mandatory quality gates before committing.
3. If a gate fails, fix the issue and re-run only the failed gate.
4. Use the project commit conventions for all changes.

<!-- crag:auto-end -->
