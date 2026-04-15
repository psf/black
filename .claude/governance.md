# Governance — black
# Inferred by crag analyze — review and adjust as needed

## Identity
- Project: black
- Stack: python, docker

## Gates (run in order, stop on failure)
### Lint
- flake8
- mypy .
- black --check .

### Test
- tox run

### Build
- python -m build

### CI (inferred from workflow)
- docker buildx imagetools create $TAGS $(printf "$REGISTRY@sha256:%s " *)
- docker buildx imagetools inspect $REGISTRY:latest
- python -m hatch build
- python -m black --check .

## Advisories (informational, not enforced)
- hadolint Dockerfile  # [ADVISORY]
- actionlint  # [ADVISORY]

## Branch Strategy
- Trunk-based development
- Free-form commits
- Commit trailer: Co-Authored-By: Claude <noreply@anthropic.com>

## Security
- No hardcoded secrets — grep for sk_live, AKIA, password= before commit

## Autonomy
- Auto-commit after gates pass

## Deployment
- Target: docker
- CI: github-actions

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

