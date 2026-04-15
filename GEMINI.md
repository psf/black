<!-- crag:auto-start -->
# GEMINI.md

> Generated from governance.md by crag. Regenerate: `crag compile --target gemini`

## Project Context

- **Name:** black
- **Stack:** python, docker
- **Runtimes:** python, docker

## Rules

### Quality Gates

Run these checks in order before committing any changes:

1. [lint] `flake8`
2. [lint] `mypy .`
3. [lint] `black --check .`
4. [test] `tox run`
5. [build] `python -m build`
6. [ci (inferred from workflow)] `docker buildx imagetools create $TAGS $(printf "$REGISTRY@sha256:%s " *)`
7. [ci (inferred from workflow)] `docker buildx imagetools inspect $REGISTRY:latest`
8. [ci (inferred from workflow)] `python -m hatch build`
9. [ci (inferred from workflow)] `python -m black --check .`

### Security

- No hardcoded secrets — grep for sk_live, AKIA, password= before commit

### Workflow

- Follow project commit conventions
- Run quality gates before committing
- Review security implications of all changes

<!-- crag:auto-end -->
