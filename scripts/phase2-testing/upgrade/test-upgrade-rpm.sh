#!/usr/bin/env bash
set -euo pipefail

: "${RPM_REPO_URL:?e.g. https://OWNER.github.io/rpm-repo}"
: "${PKG_NAME:?e.g. redoubt}"
: "${FROM_VER:?e.g. 1.0.0-1}"
: "${TO_VER:?e.g. 1.1.0-1}"
: "${RPM_GPG_URL:?URL to RELEASE-GPG-KEY}"

if ! command -v multipass >/dev/null; then echo "multipass required"; exit 2; fi

NAME="rpm-upgrade-test"
multipass launch -n "$NAME" rockylinux:9
trap 'multipass delete -p "$NAME" || true' EXIT

multipass exec "$NAME" -- bash -lc "
  set -euo pipefail
  sudo dnf install -y curl

  sudo tee /etc/yum.repos.d/redoubt.repo >/dev/null <<EOF
[redoubt]
name=Redoubt
baseurl=$RPM_REPO_URL
enabled=1
gpgcheck=1
gpgkey=$RPM_GPG_URL
EOF

  sudo dnf clean all && sudo dnf makecache

  # Install FROM
  sudo dnf install -y ${PKG_NAME}-${FROM_VER}

  # Seed config
  mkdir -p ~/.config/redoubt && echo 'key="value"' > ~/.config/redoubt/config.toml

  # Upgrade TO
  sudo dnf install -y ${PKG_NAME}-${TO_VER}
  ${PKG_NAME} --version || true
  grep -q 'key="value"' ~/.config/redoubt/config.toml

  # Rollback
  sudo dnf downgrade -y ${PKG_NAME}-${FROM_VER}
  ${PKG_NAME} --version || true
  grep -q 'key="value"' ~/.config/redoubt/config.toml
"
echo "✓ RPM upgrade/rollback OK"
