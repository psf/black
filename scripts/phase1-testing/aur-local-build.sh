#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

docker run --rm -v "$ROOT:/work" archlinux:latest bash -lc '
  set -euo pipefail
  pacman -Syu --noconfirm base-devel git sudo namcap
  useradd -m builder && echo "builder ALL=(ALL) NOPASSWD:ALL" >>/etc/sudoers
  su - builder -c "
    cd /work/packaging/aur &&
    sleep 10 &&
    makepkg -s --noconfirm &&
    namcap ./*.pkg.tar.zst || true
  "
'
echo "AUR Phase 1 OK"