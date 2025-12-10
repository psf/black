#!/usr/bin/env bash
set -euo pipefail

: "${PKG_NAME:?}"
: "${FROM_VER:?}"
: "${TO_VER:?}"
: "${APT_REPO_URL:?}"
: "${APT_DIST:=stable}"
: "${APT_COMPONENT:=main}"
: "${APT_GPG_URL:?}"
: "${RPM_REPO_URL:?}"
: "${RPM_GPG_URL:?}"
: "${IMAGE:=ghcr.io/OWNER/redoubt}"
: "${FROM_TAG:=1.0.0}"
: "${TO_TAG:=1.1.0}"
: "${SNAP_NAME:=redoubt}"
: "${FROM_CHANNEL:=edge}"
: "${TO_CHANNEL:=beta}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> PyPI"
bash "$SCRIPT_DIR/test-upgrade-pypi.sh" || true

echo "==> APT"
APT_REPO_URL="$APT_REPO_URL" APT_DIST="$APT_DIST" APT_COMPONENT="$APT_COMPONENT" APT_GPG_URL="$APT_GPG_URL" \
PKG_NAME="$PKG_NAME" FROM_VER="$FROM_VER" TO_VER="$TO_VER" \
bash "$SCRIPT_DIR/test-upgrade-apt.sh"

echo "==> RPM"
RPM_REPO_URL="$RPM_REPO_URL" RPM_GPG_URL="$RPM_GPG_URL" PKG_NAME="$PKG_NAME" FROM_VER="$FROM_VER" TO_VER="$TO_VER" \
bash "$SCRIPT_DIR/test-upgrade-rpm.sh"

echo "==> Docker"
IMAGE="$IMAGE" FROM_TAG="$FROM_TAG" TO_TAG="$TO_TAG" \
bash "$SCRIPT_DIR/test-upgrade-docker.sh"

echo "==> Snap"
SNAP_NAME="$SNAP_NAME" FROM_CHANNEL="$FROM_CHANNEL" TO_CHANNEL="$TO_CHANNEL" \
bash "$SCRIPT_DIR/test-upgrade-snap.sh"

echo "✓ Upgrade suite complete"
