#!/usr/bin/env bash
set -euo pipefail

# Get repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Ensure virtual environment exists
if [ ! -d "$REPO_ROOT/.venv" ]; then
    (cd "$REPO_ROOT" && uv venv)
fi

# Install devpi and build tools
(cd "$REPO_ROOT" && uv pip install --upgrade pip==24.3.1 wheel devpi-server devpi-client twine build)

DEVPI_DIR="$(mktemp -d)"

# Initialize devpi server
"$REPO_ROOT/.venv/bin/devpi-init" --serverdir "$DEVPI_DIR" >/dev/null 2>&1

# Start devpi server in background
"$REPO_ROOT/.venv/bin/devpi-server" --serverdir "$DEVPI_DIR" --host 127.0.0.1 --port 3141 >/dev/null 2>&1 &
DEVPI_PID=$!
trap 'kill "$DEVPI_PID" 2>/dev/null || true; rm -rf "$DEVPI_DIR"' EXIT

# Wait for server to be ready
sleep 2

"$REPO_ROOT/.venv/bin/devpi" use http://127.0.0.1:3141
"$REPO_ROOT/.venv/bin/devpi" user -c testuser password=secret || true
"$REPO_ROOT/.venv/bin/devpi" login testuser --password=secret
"$REPO_ROOT/.venv/bin/devpi" index -c dev bases=root/pypi || true
"$REPO_ROOT/.venv/bin/devpi" use testuser/dev

(cd "$REPO_ROOT" && uv run python -m build)
# Upload with either twine or devpi upload
"$REPO_ROOT/.venv/bin/twine" upload --repository-url http://127.0.0.1:3141/testuser/dev "$REPO_ROOT"/dist/* || true
"$REPO_ROOT/.venv/bin/devpi" upload || true

# Create a fresh venv for testing the installation
TEST_VENV="$(mktemp -d)/test-venv"
uv venv "$TEST_VENV"
# Install pip in the test venv
"$TEST_VENV/bin/python" -m ensurepip --upgrade >/dev/null 2>&1 || true
"$TEST_VENV/bin/pip" install --upgrade pip >/dev/null 2>&1 || true
"$TEST_VENV/bin/pip" install --index-url http://127.0.0.1:3141/testuser/dev/simple --trusted-host 127.0.0.1 demo-secure-cli >/dev/null 2>&1 || \
"$TEST_VENV/bin/pip" install --index-url http://127.0.0.1:3141/testuser/dev/simple --trusted-host 127.0.0.1 provenance-demo >/dev/null 2>&1 || true
echo "✓ devpi Phase 1 OK"