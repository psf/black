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

NAME="test-aur-archlinux-$$"

# Setup cleanup trap
vm_setup_cleanup_trap "$NAME"

# Launch VM
if ! vm_launch_with_retry "$NAME" "archlinux"; then
  echo "ERROR: Failed to launch Arch Linux VM"
  vm_lock_release
  exit 1
fi

# Transfer PKGBUILD
if ! multipass transfer packaging/aur "$NAME":/tmp/aur; then
  echo "ERROR: Failed to transfer AUR files"
  exit 1
fi

# Build and install
if multipass exec "$NAME" -- bash -lc '
  set -euo pipefail
  pacman -Syu --noconfirm base-devel git
  useradd -m b && echo "b ALL=(ALL) NOPASSWD:ALL" >>/etc/sudoers
  chown -R b:b /tmp/aur
  su - b -c "cd /tmp/aur && makepkg -si --noconfirm"
  command -v redoubt || command -v provenance-demo || true
'; then
  echo "✓ AUR Phase 2 VM OK"
  exit 0
else
  echo "✗ AUR Phase 2 VM FAILED"
  exit 1
fi