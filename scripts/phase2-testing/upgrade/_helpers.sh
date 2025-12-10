#!/usr/bin/env bash
set -euo pipefail

REDOUBT_BIN="${REDOUBT_BIN:-redoubt}"
REDOUBT_CFG="${REDOUBT_CFG:-$HOME/.config/redoubt/config.toml}"

setup_cfg() {
  mkdir -p "$(dirname "$REDOUBT_CFG")"
  printf 'key="value"\n' > "$REDOUBT_CFG"
}

assert_cfg_preserved() {
  grep -q 'key="value"' "$REDOUBT_CFG" || {
    echo "✗ Config not preserved: $REDOUBT_CFG"; exit 1;
  }
  echo "✓ Config preserved"
}
