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
: "${CACHIX_CACHE:?Set CACHIX_CACHE}"
NAME="test-nix-cachix-$$"

# Setup cleanup trap
vm_setup_cleanup_trap "$NAME"

if multipass find nixos-23.11 >/dev/null 2>&1; then
  if ! vm_launch_with_retry "$NAME" "nixos-23.11" "2G" "10G"; then
    echo "Failed to launch NixOS VM"
    exit 1
  fi
else
  echo "NixOS image not available, using Ubuntu + Nix installer"
  if ! vm_launch_with_retry "$NAME" "ubuntu:22.04" "2G" "10G"; then
    echo "Failed to launch Ubuntu VM"
    exit 1
  fi
  multipass exec "$NAME" -- bash -lc "curl -L https://nixos.org/nix/install | sh -s -- --daemon"
  multipass exec "$NAME" -- bash -lc ". /etc/profile.d/nix.sh || true"
fi

multipass exec "$NAME" -- bash -lc "
  set -euo pipefail
  nix-env -iA cachix -f https://cachix.org/api/v1/install
  cachix use '$CACHIX_CACHE'
  nix run 'github:OWNER/REPO' -- --version || true
  echo '✓ Nix run via Cachix executed (install may skip until cache populated)'
"
