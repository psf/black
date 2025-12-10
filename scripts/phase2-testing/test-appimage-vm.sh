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

# Find AppImage
APPIMAGE="$(ls -1 redoubt-*.AppImage 2>/dev/null | head -n1 || true)"
if [ -z "$APPIMAGE" ]; then
  echo "ERROR: No AppImage found"
  vm_lock_release
  exit 1
fi

echo "Testing AppImage: $APPIMAGE"
echo ""

# Test on multiple distributions
FAILED=0
for VM in ubuntu:22.04 debian:12 fedora:40; do
  NAME="test-appimage-${VM//[:.]/-}-$$"

  echo "Testing on $VM..."

  # Launch VM with retries
  if ! vm_launch_with_retry "$NAME" "$VM"; then
    echo "Failed to launch $VM"
    FAILED=$((FAILED + 1))
    continue
  fi

  # Transfer AppImage
  if ! multipass transfer "$APPIMAGE" "$NAME":; then
    echo "Failed to transfer AppImage to $NAME"
    vm_cleanup "$NAME"
    FAILED=$((FAILED + 1))
    continue
  fi

  # Test AppImage
  if multipass exec "$NAME" -- bash -lc "chmod +x $APPIMAGE && ./$APPIMAGE --version"; then
    echo "✓ OK on $VM"
  else
    echo "✗ FAILED on $VM"
    FAILED=$((FAILED + 1))
  fi

  # Clean up VM immediately after test
  vm_cleanup "$NAME"
  echo ""
done

# Release lock
vm_lock_release

if [ $FAILED -gt 0 ]; then
  echo "AppImage Phase 2 VM FAILED ($FAILED failures)"
  exit 1
else
  echo "AppImage Phase 2 VM OK"
  exit 0
fi