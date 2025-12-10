#!/usr/bin/env bash
set -euo pipefail

echo "Validating testing environment..."
MISSING=()
for bin in docker multipass gpg python3; do
  command -v "$bin" >/dev/null || MISSING+=("$bin")
done

if (( ${#MISSING[@]} )); then
  echo "Missing required tools: ${MISSING[*]}"
  echo "See: docs/testing/ENVIRONMENT-SETUP.md"
  exit 1
fi
echo "✓ Required tools present"

OPTIONAL=()
command -v nix >/dev/null || OPTIONAL+=("nix (for Nix tests)")
command -v flatpak-builder >/dev/null || OPTIONAL+=("flatpak-builder (for Flatpak)")
(( ${#OPTIONAL[@]} )) && echo "⚠ Optional tools missing: ${OPTIONAL[*]}"
