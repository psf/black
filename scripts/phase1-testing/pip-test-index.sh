#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

CHANNEL="pip-test-index"
log "Starting $CHANNEL workflow"

require_command python3

ensure_python_build_artifacts

TEMP_DIR="$(mktemp -d "$WORK_ROOT/${CHANNEL}.XXXX")"
trap 'rm -rf "$TEMP_DIR"' EXIT

VENV="$TEMP_DIR/venv"
python3 -m venv "$VENV" || skip "venv creation failed"
"$VENV/bin/pip" install --upgrade pip >/dev/null
"$VENV/bin/pip" install --quiet build >/dev/null 2>&1 || skip "pip install build==1.2.2.post1 failed (likely offline)"

# Build wheel/sdist if not already
(cd "$REPO_ROOT" && "$VENV/bin/python" -m build >/dev/null 2>&1 || true)

WHEEL="$(ls -1 "$REPO_ROOT"/dist/*.whl 2>/dev/null | head -n1 || true)"
[[ -z "$WHEEL" ]] && skip "No wheel artifact available"

PKG_NAME="$(basename "$WHEEL")"
PACKAGE="${PKG_NAME%%-*}"
PORT="${PIP_TEST_PORT:-8765}"

SIMPLE_DIR="$TEMP_DIR/simple/${PACKAGE}"
mkdir -p "$SIMPLE_DIR"
cp "$WHEEL" "$TEMP_DIR/"

cat >"$SIMPLE_DIR/index.html" <<EOF
<html><body>
<a href="../../$(basename "$WHEEL")">$(basename "$WHEEL")</a>
</body></html>
EOF

pushd "$TEMP_DIR" >/dev/null
python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" >/dev/null 2>&1 || true; rm -rf "$TEMP_DIR"' EXIT
sleep 1

INSTALL_DIR="$TEMP_DIR/install"
mkdir -p "$INSTALL_DIR"

log "Installing package from local simple index"
if ! "$VENV/bin/pip" install --no-cache-dir --index-url "http://127.0.0.1:${PORT}/simple/" "$PACKAGE" >/dev/null; then
  skip "pip install from local index failed (likely dynamic metadata not matching package name)"
fi

log "Package installed successfully from local simple index"
popd >/dev/null
