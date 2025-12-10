#!/usr/bin/env bash
set -euo pipefail

: "${APT_REPO_URL:?e.g. https://OWNER.github.io/deb-repo}"
: "${APT_DIST:?e.g. stable}"
: "${APT_COMPONENT:?e.g. main}"
: "${PKG_NAME:?e.g. redoubt}"
: "${FROM_VER:?e.g. 1.0.0-1}"
: "${TO_VER:?e.g. 1.1.0-1}"
: "${APT_GPG_URL:?URL to release.pub.asc}"

if ! command -v multipass >/dev/null; then echo "multipass required"; exit 2; fi

NAME="apt-upgrade-test"
multipass launch -n "$NAME" ubuntu:22.04
trap 'multipass delete -p "$NAME" || true' EXIT

multipass exec "$NAME" -- bash -lc "
  set -euo pipefail
  sudo apt update
  curl -fsSL '$APT_GPG_URL' | sudo tee /usr/share/keyrings/redoubt.asc >/dev/null
  echo 'deb [signed-by=/usr/share/keyrings/redoubt.asc] $APT_REPO_URL $APT_DIST $APT_COMPONENT' | \
    sudo tee /etc/apt/sources.list.d/redoubt.list
  sudo apt update

  # Install FROM
  sudo apt install -y ${PKG_NAME}=${FROM_VER}

  # Seed config
  mkdir -p ~/.config/redoubt && echo 'key="value"' > ~/.config/redoubt/config.toml

  # Upgrade TO
  sudo apt install -y ${PKG_NAME}=${TO_VER}
  ${PKG_NAME} --version || true
  grep -q 'key="value"' ~/.config/redoubt/config.toml

  # Rollback TO FROM
  sudo apt install -y ${PKG_NAME}=${FROM_VER}
  ${PKG_NAME} --version || true
  grep -q 'key="value"' ~/.config/redoubt/config.toml
"
echo "✓ APT upgrade/rollback OK"
