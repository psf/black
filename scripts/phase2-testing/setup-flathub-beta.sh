#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if ! command -v flatpak-builder >/dev/null; then
  echo "flatpak-builder not installed. Install with:"
  echo "  apt install flatpak-builder (Debian/Ubuntu)"
  echo "  dnf install flatpak-builder (Fedora)"
  exit 2
fi

echo "Setting up Flathub Beta remote..."

# Add Flathub Beta remote
flatpak remote-add --if-not-exists flathub-beta https://flathub.org/beta-repo/flathub-beta.flatpakrepo --user || \
  flatpak remote-add --if-not-exists flathub-beta https://flathub.org/beta-repo/flathub-beta.flatpakrepo

# Validate and build Flatpak manifest
echo "Building Flatpak from manifest..."
BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "$BUILD_DIR"' EXIT

flatpak-builder --user --force-clean --repo="$ROOT_DIR/flatpak-beta-repo" "$BUILD_DIR" packaging/flatpak/com.OWNER.Redoubt.yml || {
  echo "❌ Flatpak build failed"
  exit 1
}

echo "Creating local Flathub Beta simulation repo..."

# Initialize local ostree repo if needed
if [[ ! -d flatpak-beta-repo ]]; then
  ostree --repo=./flatpak-beta-repo init --mode=archive-z2
fi

# Export build to local repo
flatpak build-export flatpak-beta-repo "$BUILD_DIR" || true

echo "✅ Local Flathub Beta simulation ready at ./flatpak-beta-repo"
echo ""
echo "To test locally:"
echo "  flatpak --user remote-add --no-gpg-verify local-beta file://$(pwd)/flatpak-beta-repo"
echo "  flatpak --user install local-beta com.OWNER.Redoubt"
echo ""
echo "For real Flathub Beta publishing:"
echo "  1. Fork flathub/flatpak repository"
echo "  2. Add your manifest as beta/com.OWNER.Redoubt.yml"
echo "  3. Open PR to Flathub Beta"
