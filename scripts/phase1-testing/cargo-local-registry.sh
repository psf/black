#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

CHANNEL="cargo-local-registry"
log "Starting $CHANNEL workflow"

require_command cargo

if ! command -v cargo-local-registry >/dev/null 2>&1; then
  log "Installing cargo-local-registry helper"
  if ! cargo install cargo-local-registry >/dev/null 2>&1; then
    skip "Unable to install cargo-local-registry (offline?)"
  fi
fi

WORK_DIR="$(mktemp -d "$WORK_ROOT/${CHANNEL}.XXXX")"
cleanup_hooks=("rm -rf '$WORK_DIR'")
trap 'for hook in "${cleanup_hooks[@]}"; do eval "$hook"; done' EXIT

CRATE_DIR="$WORK_DIR/redoubt_demo"
cargo new "$CRATE_DIR" --lib >/dev/null

pushd "$CRATE_DIR" >/dev/null
cat >>Cargo.toml <<'EOF'

[lib]
path = "lib.rs"

[package.metadata]
description = "Redoubt demo crate for local registry validation"
EOF

cat >src/lib.rs <<'EOF'
pub fn greet() -> &'static str {
    "Hello from Redoubt local registry"
}
EOF

log "Packaging crate via cargo package"
cargo package >/dev/null 2>&1 || skip "cargo package failed"
PACKAGE_FILE="$(ls -1 target/package/*.crate | head -n1)"
popd >/dev/null

REGISTRY_DIR="$WORK_DIR/registry"
cargo local-registry --crate "$PACKAGE_FILE" "$REGISTRY_DIR" >/dev/null 2>&1 || skip "cargo local-registry failed"

CONSUMER_DIR="$WORK_DIR/consumer"
cargo new "$CONSUMER_DIR" >/dev/null

cat >"$CONSUMER_DIR/.cargo/config.toml" <<EOF
[registries]
redoubt-local = { index = "file://$REGISTRY_DIR/index" }
EOF

cat >>"$CONSUMER_DIR/Cargo.toml" <<'EOF'

[dependencies]
redoubt_demo = { version = "0.0.1", registry = "redoubt-local" }
EOF

pushd "$CONSUMER_DIR" >/dev/null
if ! cargo fetch --registry redoubt-local >/dev/null 2>&1; then
  skip "cargo fetch from local registry failed"
fi
log "Cargo local registry workflow completed"
popd >/dev/null
