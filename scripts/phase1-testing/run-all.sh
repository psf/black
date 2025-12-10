#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[dist-test] Running all distribution test harnesses"

EXIT_CODE=0

for script in "$SCRIPT_DIR"/*.sh; do
  [[ "$(basename "$script")" == "common.sh" ]] && continue
  [[ "$(basename "$script")" == "run-all.sh" ]] && continue
  [[ "$(basename "$script")" == "run-all-no-skips.sh" ]] && continue
  echo "[dist-test] >>> $(basename "$script")"
  if ! "$script"; then
    echo "[dist-test] <<< $(basename "$script") FAILED"
    EXIT_CODE=1
  else
    echo "[dist-test] <<< $(basename "$script") DONE"
  fi
done

if command -v pwsh >/dev/null 2>&1; then
  for ps1 in "$SCRIPT_DIR"/*.ps1; do
    echo "[dist-test] >>> $(basename "$ps1")"
    if ! pwsh "$ps1"; then
      echo "[dist-test] <<< $(basename "$ps1") FAILED"
      EXIT_CODE=1
    else
      echo "[dist-test] <<< $(basename "$ps1") DONE"
    fi
  done
else
  echo "[dist-test] PowerShell not available; skipping *.ps1 scripts"
fi

exit "$EXIT_CODE"
