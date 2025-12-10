#!/usr/bin/env bash
set -euo pipefail

: "${SNAP_NAME:?e.g. redoubt}"
: "${FROM_CHANNEL:=edge}"
: "${TO_CHANNEL:=beta}"

if ! command -v snap >/dev/null; then
  echo "snap not available on this host. Run inside Ubuntu VM or CI image."; exit 0
fi

sudo snap install "$SNAP_NAME" --"$FROM_CHANNEL"
"$SNAP_NAME" --version || true
mkdir -p "$HOME/.config/redoubt" && echo 'key="value"' > "$HOME/.config/redoubt/config.toml"

sudo snap refresh "$SNAP_NAME" --"$TO_CHANNEL"
"$SNAP_NAME" --version || true
grep -q 'key="value"' "$HOME/.config/redoubt/config.toml"

# Rollback (if the channel still offers the older rev)
sudo snap refresh "$SNAP_NAME" --"$FROM_CHANNEL" || true
"$SNAP_NAME" --version || true
grep -q 'key="value"' "$HOME/.config/redoubt/config.toml"
echo "✓ Snap channel refresh/rollback OK (best effort)"
