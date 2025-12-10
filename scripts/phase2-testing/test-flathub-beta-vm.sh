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
NAME="test-flatpak-beta-ubuntu2404-$$"

# Setup cleanup trap
vm_setup_cleanup_trap "$NAME"

if ! vm_launch_with_retry "$NAME" "ubuntu:24.04" "2G" "10G"; then
    echo "Failed to launch VM"
    exit 1
fi

multipass exec "$NAME" -- bash -lc '
  set -euo pipefail
  sudo apt update && sudo apt install -y flatpak gnome-software-plugin-flatpak ca-certificates curl
  flatpak remote-add --if-not-exists flathub-beta https://flathub.org/beta-repo/flathub-beta.flatpakrepo
  # Replace APP_ID with your actual ID once published
  APP_ID="com.OWNER.Redoubt"
  echo "Flatpak beta remote configured. To fully test:"
  echo "  flatpak install -y flathub-beta $APP_ID"
  echo "  flatpak run $APP_ID --version"
'
echo "✓ Flatpak VM prepared for beta install"
