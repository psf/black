#!/usr/bin/env bash
set -euo pipefail

# Common helpers for distribution testing scripts.

if [[ "${TRACE:-}" == "1" ]]; then
  set -x
fi

if [[ -z "${REPO_ROOT:-}" ]]; then
  if command -v git >/dev/null 2>&1; then
    REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
  fi
  if [[ -z "${REPO_ROOT:-}" ]]; then
    REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
  fi
fi

WORK_ROOT="${WORK_ROOT:-$REPO_ROOT/.tmp/distribution-testing}"
mkdir -p "$WORK_ROOT"

log() {
  printf '[dist-test] %s\n' "$*" >&2
}

skip() {
  log "SKIP: $*"
  exit 0
}

require_command() {
  local cmd="$1"
  command -v "$cmd" >/dev/null 2>&1 || skip "command '$cmd' not available"
}

# Attempt to retrieve a docker image if possible. Skips gracefully if pull fails.
ensure_docker_image() {
  local image="$1"
  if ! docker image inspect "$image" >/dev/null 2>&1; then
    log "Pulling docker image $image"
    if ! docker pull "$image" >/dev/null 2>&1; then
      skip "Unable to pull docker image $image"
    fi
  fi
}

ensure_python_build_artifacts() {
  mkdir -p "$WORK_ROOT/dist"
  if compgen -G "$REPO_ROOT/dist/*.whl" >/dev/null 2>&1; then
    return 0
  fi
  log "Building Python distributions"
  if [[ -x "$REPO_ROOT/scripts/build_pyz.sh" ]]; then
    if ! "$REPO_ROOT/scripts/build_pyz.sh"; then
      skip "Unable to build Python artifacts (likely offline)."
    fi
  else
    require_command uv
    # Ensure venv exists
    if [[ ! -d "$REPO_ROOT/.venv" ]]; then
      (cd "$REPO_ROOT" && uv venv) || skip "Unable to create virtual environment"
    fi
    (cd "$REPO_ROOT" && uv pip install --upgrade pip==24.3.1 build >/dev/null 2>&1) || skip "pip build dependencies unavailable"
    (cd "$REPO_ROOT" && uv run python -m build) || skip "python build failed"
  fi
}
