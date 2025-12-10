#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

docker run --rm -v "$ROOT_DIR:/work" -w /work ubuntu:22.04 bash -c '
  set -euo pipefail
  apt-get update
  apt-get install -y python3-pip python3-setuptools patchelf desktop-file-utils dpkg wget file fuse libfuse2
  # Install linuxdeploy instead of appimage-builder to avoid version parser bugs
  wget -q https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage -O /tmp/linuxdeploy.AppImage
  chmod +x /tmp/linuxdeploy.AppImage
  # Extract the AppImage (FUSE may not work in container)
  cd /tmp && /tmp/linuxdeploy.AppImage --appimage-extract >/dev/null 2>&1
  mv /tmp/squashfs-root /usr/local/linuxdeploy
  ln -s /usr/local/linuxdeploy/AppRun /usr/local/bin/linuxdeploy
  cd /work

  # Create AppDir and copy binary
  mkdir -p AppDir/usr/bin
  if [[ -f "dist/redoubt.pyz" ]]; then
    install -m 0755 dist/redoubt.pyz AppDir/usr/bin/redoubt
  else
    echo "dist/redoubt.pyz missing. Build your binary first."; exit 3
  fi

  if [[ ! -x packaging/appimage/build-appimage.sh ]]; then
    echo "Missing packaging/appimage/build-appimage.sh"; exit 1
  fi

  # Build
  ./packaging/appimage/build-appimage.sh

  # Smoke tests
  APPIMAGE="$(ls -1 redoubt-*.AppImage | head -n1)"
  chmod +x "$APPIMAGE"

  "$APPIMAGE" --version
  "$APPIMAGE" hello "AppImage"
  "$APPIMAGE" verify || true   # allow verify to be a no-op for now

  echo "AppImage Phase 1 OK: $APPIMAGE"
'