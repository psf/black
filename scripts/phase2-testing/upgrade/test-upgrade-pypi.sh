#!/usr/bin/env bash
set -euo pipefail

: "${PKG_NAME:?e.g. demo-secure-cli or redoubt}"
: "${FROM_VER:?e.g. 1.0.0}"
: "${TO_VER:?e.g. 1.1.0}"

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$DIR/_helpers.sh"

python -m venv .venv && . .venv/bin/activate
pip install -U pip==24.3.1

# Install FROM version
pip install "${PKG_NAME}==${FROM_VER}"

# Find installed CLI name
REDOUBT_BIN="${REDOUBT_BIN:-$(python - <<'PY'
import shutil,sys
print(shutil.which("redoubt") or shutil.which("provenance-demo") or "redoubt")
PY
)}"

# Seed config
setup_cfg

# Upgrade to TO version
pip install --upgrade "${PKG_NAME}==${TO_VER}"
"$REDOUBT_BIN" --version || true
assert_cfg_preserved

# Rollback check
pip install --upgrade "${PKG_NAME}==${FROM_VER}"
"$REDOUBT_BIN" --version || true
assert_cfg_preserved

echo "✓ PyPI upgrade/rollback OK"
