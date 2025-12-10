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
: "${GEM_NAME:?e.g. redoubt}"
NAME="test-gems-ghpkgs-$$"

# Setup cleanup trap
vm_setup_cleanup_trap "$NAME"

if ! vm_launch_with_retry "$NAME" "ubuntu:22.04" "2G" "10G"; then
    echo "Failed to launch VM"
    exit 1
fi

multipass exec "$NAME" -- bash -lc "
  set -euo pipefail
  apt-get update && apt-get install -y ruby-full build-essential
  # GitHub Packages host: rubygems.pkg.github.com/OWNER
  gem sources --add https://rubygems.pkg.github.com/OWNER --remove https://rubygems.org/ || true
  echo 'Install attempt (may skip if not published yet):'
  gem install '$GEM_NAME' || true
  echo '✓ RubyGems GH Packages VM path executed'
"
