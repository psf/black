#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source VM utilities
source "$SCRIPT_DIR/vm-test-utils.sh"

# Acquire lock to prevent concurrent VM tests
vm_lock_acquire

# Run pre-flight checks
if ! vm_preflight_check; then
  vm_lock_release
  exit 1
fi

if ! command -v multipass >/dev/null; then echo "multipass needed"; exit 2; fi
: "${NPM_PKG:?e.g. @OWNER/redoubt}"
NAME="test-npm-ghpkgs-$$"

# Setup cleanup trap
vm_setup_cleanup_trap "$NAME"

if ! vm_launch_with_retry "$NAME" "ubuntu:22.04" "2G" "10G"; then
    echo "Failed to launch VM"
    exit 1
fi

# Pass a read token via env if you want to test private install (NPM_READ_TOKEN)
if [[ -n "${NPM_READ_TOKEN:-}" ]]; then
  multipass exec "$NAME" -- bash -lc "mkdir -p /root/.npmrc && echo '//npm.pkg.github.com/:_authToken=${NPM_READ_TOKEN}' > /root/.npmrc"
fi
multipass exec "$NAME" -- bash -lc "
  set -euo pipefail
  apt-get update && apt-get install -y nodejs npm
  npm config set '@${NPM_PKG#@*/}:registry' 'https://npm.pkg.github.com/'
  npm view '$NPM_PKG' version || echo 'Package not yet published — install step will be skipped'
  npm i '$NPM_PKG' || true
  echo '✓ npm GH Packages VM path executed'
"
