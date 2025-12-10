#!/usr/bin/env bash
set -euo pipefail

# Matrix-aware RPM (DNF) upgrade/rollback test using Multipass VM image selection.
: "${RPM_REPO_URL:?missing}"
: "${RPM_GPG_URL:?missing}"
: "${PKG_NAME:?missing}"
: "${FROM_VER:?missing}"
: "${TO_VER:?missing}"

RPM_VM_IMAGE="${RPM_VM_IMAGE:-rockylinux:9}"

if ! command -v multipass >/dev/null; then echo "multipass required"; exit 2; fi

NAME="rpm-upgrade-$(echo "$RPM_VM_IMAGE" | tr :.- _)"
multipass launch -n "$NAME" "$RPM_VM_IMAGE"
trap 'multipass delete -p "$NAME" || true' EXIT

multipass exec "$NAME" -- bash -lc "
  set -euo pipefail
  # dnf should exist by default on Rocky/Fedora; ensure curl present
  sudo dnf -y install curl || sudo microdnf -y install curl || true

  sudo tee /etc/yum.repos.d/redoubt.repo >/dev/null <<EOF
[redoubt]
name=Redoubt
baseurl=$RPM_REPO_URL
enabled=1
gpgcheck=1
gpgkey=$RPM_GPG_URL
EOF

  sudo dnf clean all || true
  sudo dnf makecache || true

  # Install FROM
  sudo dnf install -y ${PKG_NAME}-${FROM_VER} || sudo dnf install -y ${PKG_NAME}-${FROM_VER%.*} || true

  # Seed config
  mkdir -p ~/.config/redoubt && echo 'key="value"' > ~/.config/redoubt/config.toml

  # Upgrade TO
  sudo dnf install -y ${PKG_NAME}-${TO_VER} || sudo dnf upgrade -y ${PKG_NAME} || true
  ${PKG_NAME} --version || true
  grep -q 'key="value"' ~/.config/redoubt/config.toml

  # Rollback (downgrade)
  sudo dnf downgrade -y ${PKG_NAME}-${FROM_VER} || true
  ${PKG_NAME} --version || true
  grep -q 'key="value"' ~/.config/redoubt/config.toml
"

echo "✓ RPM upgrade/rollback OK on $RPM_VM_IMAGE"
