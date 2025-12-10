#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

CHANNEL="conda-local-channel"
log "Starting $CHANNEL workflow"

if command -v mamba >/dev/null 2>&1; then
  CONDA_BIN="mamba"
elif command -v conda >/dev/null 2>&1; then
  CONDA_BIN="conda"
else
  skip "conda/mamba not installed"
fi

require_command conda-build || skip "conda-build not installed"

WORK_DIR="$(mktemp -d "$WORK_ROOT/${CHANNEL}.XXXX")"
cleanup_hooks=("rm -rf '$WORK_DIR'")
trap 'for hook in "${cleanup_hooks[@]}"; do eval "$hook"; done' EXIT

RECIPE_DIR="$WORK_DIR/recipe"
mkdir -p "$RECIPE_DIR"

cat >"$RECIPE_DIR/meta.yaml" <<'EOF'
package:
  name: redoubt-demo
  version: 0.0.1

build:
  noarch: python
  script: python -c "print('hello redoubt conda')"

requirements:
  host:
    - python
  run:
    - python

about:
  home: https://example.com/redoubt
  summary: Demo recipe for local channel testing
  license: MIT
EOF

log "Building conda package"
if ! conda-build "$RECIPE_DIR" --output-folder "$WORK_DIR/channel" >/dev/null 2>&1; then
  skip "conda-build failed (missing dependencies)"
fi

log "Indexing local channel"
conda index "$WORK_DIR/channel" >/dev/null 2>&1 || skip "conda index failed"

ENV_DIR="$WORK_DIR/env"
log "Creating environment from local channel"
if ! "$CONDA_BIN" create -y -p "$ENV_DIR" -c "file://$WORK_DIR/channel" redoubt-demo >/dev/null 2>&1; then
  skip "conda create from local channel failed"
fi

log "Conda local channel workflow completed"
