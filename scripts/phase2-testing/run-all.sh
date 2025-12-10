#!/usr/bin/env bash
# Quick wrapper to run comprehensive VM tests
# Alias for comprehensive-vm-tests.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "═══════════════════════════════════════════════════════════════════"
echo "  Phase 2: Individual VM Testing"
echo "  Running: comprehensive-vm-tests.sh"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

exec "$SCRIPT_DIR/comprehensive-vm-tests.sh"
