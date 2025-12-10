#!/usr/bin/env bash
set -euo pipefail
: "${CACHIX_CACHE:?Set CACHIX_CACHE name}"
: "${CACHIX_TOKEN:?Set CACHIX_TOKEN}"

if ! command -v cachix >/dev/null; then
  nix-env -iA cachix -f https://cachix.org/api/v1/install
fi

cachix authtoken "$CACHIX_TOKEN"
cachix use "$CACHIX_CACHE"
echo "✓ Cachix configured for cache: $CACHIX_CACHE"
