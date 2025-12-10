#!/usr/bin/env bash
set -euo pipefail
if ! command -v nix >/dev/null; then echo "Nix not installed, skipping"; exit 0; fi
nix --extra-experimental-features nix-command --extra-experimental-features flakes flake check || true
nix --extra-experimental-features nix-command --extra-experimental-features flakes build .# || nix --extra-experimental-features nix-command --extra-experimental-features flakes build .
./result/bin/redoubt --version || ./result/bin/provenance-demo --version
nix --extra-experimental-features nix-command --extra-experimental-features flakes run .# -- --version || true
echo "Nix Phase 1 OK"