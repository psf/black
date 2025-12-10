#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$ROOT_DIR"

echo "=== AppImage Build Test with linuxdeploy (Phase 2 VM) ==="
echo ""

# Check if .pyz exists
if [ ! -f "dist/redoubt.pyz" ]; then
  echo "Building .pyz first..."
  bash scripts/build_pyz.sh
fi

# Source VM utilities
source "$SCRIPT_DIR/vm-test-utils.sh"

# Acquire lock
vm_lock_acquire

# Run pre-flight checks
if ! vm_preflight_check; then
  vm_lock_release
  exit 1
fi

VM_NAME="test-appimage-build-$$"
echo "Creating VM: $VM_NAME"

# Launch Ubuntu 22.04 VM
if ! vm_launch_with_retry "$VM_NAME" "22.04"; then
  echo "Failed to launch VM"
  vm_lock_release
  exit 1
fi

# Install dependencies
echo "Installing dependencies in VM..."
multipass exec "$VM_NAME" -- bash -c '
  sudo apt-get update -qq
  sudo apt-get install -y -qq wget fuse libfuse2 patchelf file
'

# Download linuxdeploy in VM (detect architecture)
echo "Downloading linuxdeploy..."
multipass exec "$VM_NAME" -- bash -c '
  ARCH=$(uname -m)
  if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
    wget -q https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-aarch64.AppImage -O /tmp/linuxdeploy
  else
    wget -q https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage -O /tmp/linuxdeploy
  fi
  chmod +x /tmp/linuxdeploy
  sudo mv /tmp/linuxdeploy /usr/local/bin/linuxdeploy
'

# Transfer files to VM
echo "Transferring .pyz to VM..."
multipass transfer dist/redoubt.pyz "$VM_NAME":

echo "Transferring desktop file and icon..."
multipass transfer packaging/appimage/redoubt.desktop "$VM_NAME":
multipass transfer packaging/appimage/icons/redoubt.png "$VM_NAME":

# Build AppImage directly in VM using linuxdeploy
echo "Building AppImage with linuxdeploy..."
if multipass exec "$VM_NAME" -- bash -c '
  # Create AppDir structure
  mkdir -p AppDir/usr/bin
  install -m 0755 redoubt.pyz AppDir/usr/bin/redoubt

  # Set architecture for appimagetool
  export ARCH=$(uname -m)
  OUT="redoubt-$(date +%Y.%m.%d)-${ARCH}.AppImage"

  # Build AppImage with linuxdeploy using transferred assets
  linuxdeploy --appdir AppDir \
    --desktop-file redoubt.desktop \
    --icon-file redoubt.png \
    --output appimage

  # Rename output
  if ls *.AppImage 1> /dev/null 2>&1; then
    for f in *.AppImage; do
      if [ -f "$f" ]; then
        mv -f "$f" "$OUT"
        echo "Built: $OUT"
        break
      fi
    done
  else
    echo "ERROR: No AppImage created"
    exit 1
  fi
'; then
  echo "✓ AppImage build successful"
else
  echo "✗ AppImage build failed"
  vm_cleanup "$VM_NAME"
  vm_lock_release
  exit 1
fi

# Test the built AppImage
echo "Testing built AppImage..."
if multipass exec "$VM_NAME" -- bash -c '
  APPIMAGE=$(ls -1 redoubt-*.AppImage 2>/dev/null | head -n1)
  if [ -z "$APPIMAGE" ]; then
    echo "ERROR: No AppImage found after build"
    exit 1
  fi

  chmod +x "$APPIMAGE"
  ./"$APPIMAGE" --version
  ./"$APPIMAGE" --help
'; then
  echo "✓ AppImage execution successful"
else
  echo "✗ AppImage execution failed"
  vm_cleanup "$VM_NAME"
  vm_lock_release
  exit 1
fi

# Transfer AppImage back to host
echo "Transferring AppImage back to host..."
APPIMAGE_NAME=$(multipass exec "$VM_NAME" -- bash -c 'ls -1 redoubt-*.AppImage 2>/dev/null | head -n1')
if [ -n "$APPIMAGE_NAME" ]; then
  multipass transfer "$VM_NAME":"$APPIMAGE_NAME" .
  echo "✓ AppImage saved: $APPIMAGE_NAME"
else
  echo "✗ Failed to find AppImage to transfer"
fi

# Clean up VM
vm_cleanup "$VM_NAME"
vm_lock_release

echo ""
echo "=== AppImage Build Test with linuxdeploy: SUCCESS ==="
echo ""
echo "Next: Run scripts/phase2-testing/test-appimage-vm.sh to test on multiple distros"
