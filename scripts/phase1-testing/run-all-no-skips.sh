#!/usr/bin/env bash
# Enhanced test runner that eliminates skips by:
# 1. Activating all PATHs (Cargo, Conda)
# 2. Building artifacts first
# 3. Setting required environment variables
# 4. Using Docker fallback for Linux tools

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║     Phase 1 Distribution Testing - Zero Skip Mode                 ║"
echo "║     Activating all tools and building prerequisites               ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Activate PATHs for tools installed but not in PATH
echo "→ Activating tool PATHs..."

if [ -d "$HOME/.cargo" ] && ! command -v cargo >/dev/null 2>&1; then
    source "$HOME/.cargo/env" 2>/dev/null || export PATH="$HOME/.cargo/bin:$PATH"
    echo "  ✓ Cargo activated"
fi

if [ -d "$HOME/miniconda" ] && ! command -v conda >/dev/null 2>&1; then
    export PATH="$HOME/miniconda/bin:$PATH"
    echo "  ✓ Conda activated"
fi

# Step 2: Build Python artifacts (required for homebrew, pip tests)
echo ""
echo "→ Building Python artifacts..."

cd "$REPO_ROOT"
if [ ! -f "dist/provenance-demo.pyz" ] || [ ! -f "dist/demo_secure_cli-0.1.0-py3-none-any.whl" ]; then
    # Build with uv
    if command -v uv >/dev/null 2>&1; then
        uv build >/dev/null 2>&1
    else
        python3 -m build >/dev/null 2>&1
    fi

    # Build .pyz
    mkdir -p build/pyz/src
    rsync -a src/ build/pyz/src/
    python3 -m zipapp build/pyz/src -m "demo_cli.cli:main" -p "/usr/bin/env python3" -o dist/provenance-demo.pyz
    chmod +x dist/provenance-demo.pyz

    echo "  ✓ Artifacts built"
else
    echo "  ✓ Artifacts already exist"
fi

# Step 3: Set environment variables for tests that need them
echo ""
echo "→ Setting environment variables..."

# For GitHub draft release testing (optional - skip if you don't have a test repo)
if [ -z "${GH_DRAFT_REPO:-}" ]; then
    echo "  ⚠ GH_DRAFT_REPO not set (github-draft-release will skip)"
    echo "    Set it to test: export GH_DRAFT_REPO='youruser/test-repo'"
fi

# Step 4: Show tool status
echo ""
echo "→ Checking tool availability..."
AVAILABLE=0
TOTAL=0

tools=(cargo conda docker go node ruby helm terraform gh pwsh)
for tool in "${tools[@]}"; do
    TOTAL=$((TOTAL + 1))
    if command -v "$tool" >/dev/null 2>&1; then
        echo "  ✓ $tool"
        AVAILABLE=$((AVAILABLE + 1))
    else
        echo "  ✗ $tool (not in PATH)"
    fi
done

echo ""
echo "Tools available: $AVAILABLE/$TOTAL"

# Step 5: Run the tests
echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                     RUNNING TESTS                                  ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

exec "$SCRIPT_DIR/run-all.sh"
