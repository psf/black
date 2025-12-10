#!/usr/bin/env bash
set -euo pipefail

# Matrix-aware APT upgrade/rollback test using Multipass VM image selection.
: "${APT_REPO_URL:?missing}"
: "${APT_DIST:?missing}"
: "${APT_COMPONENT:?missing}"
: "${APT_GPG_URL:?missing}"
: "${PKG_NAME:?missing}"
: "${FROM_VER:?missing}"
: "${TO_VER:?missing}"

APT_VM_IMAGE="${APT_VM_IMAGE:-ubuntu:22.04}"

if ! command -v multipass >/dev/null; then echo "multipass required"; exit 2; fi

NAME="apt-upgrade-$(echo "$APT_VM_IMAGE" | tr :.- _)"
multipass launch -n "$NAME" "$APT_VM_IMAGE"
trap 'multipass delete -p "$NAME" || true' EXIT

multipass exec "$NAME" -- bash -lc "
  set -euo pipefail
  export DEBIAN_FRONTEND=noninteractive
  (command -v apt >/dev/null && sudo apt update) || true
  sudo apt-get update || true
  sudo apt-get install -y curl ca-certificates || true

  # Add repo key and entry
  curl -fsSL '$APT_GPG_URL' | sudo tee /usr/share/keyrings/redoubt.asc >/dev/null
  echo 'deb [signed-by=/usr/share/keyrings/redoubt.asc] $APT_REPO_URL $APT_DIST $APT_COMPONENT' | \
    sudo tee /etc/apt/sources.list.d/redoubt.list
  sudo apt-get update

  # Install FROM
  sudo apt-get install -y ${PKG_NAME}=${FROM_VER}

  # Seed config
  mkdir -p ~/.config/redoubt && echo 'key="value"' > ~/.config/redoubt/config.toml

  # Upgrade TO
  sudo apt-get install -y ${PKG_NAME}=${TO_VER}
  ${PKG_NAME} --version || true
  grep -q 'key="value"' ~/.config/redoubt/config.toml

  # Rollback TO FROM
  sudo apt-get install -y ${PKG_NAME}=${FROM_VER}
  ${PKG_NAME} --version || true
  grep -q 'key="value"' ~/.config/redoubt/config.toml
"

echo "✓ APT upgrade/rollback OK on $APT_VM_IMAGE"
