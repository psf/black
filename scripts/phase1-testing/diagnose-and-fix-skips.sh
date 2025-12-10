#!/usr/bin/env bash
# Diagnose and fix all Phase 1 test skips
# This installs missing sub-commands and fixes configuration issues

set -euo pipefail

echo "═══════════════════════════════════════════════════════════════════"
echo "  Phase 1 Skip Diagnosis & Fix Script"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Activate PATHs
source ~/.cargo/env 2>/dev/null || export PATH="$HOME/.cargo/bin:$PATH"
export PATH="$HOME/miniconda/bin:$PATH"

# 1. Conda - missing conda-build
echo "→ Checking Conda..."
if command -v conda >/dev/null 2>&1; then
    if ! command -v conda-build >/dev/null 2>&1; then
        echo "  Installing conda-build..."
        conda install -y conda-build -c conda-forge >/dev/null 2>&1 && echo "  ✓ conda-build installed"
    else
        echo "  ✓ conda-build already installed"
    fi
else
    echo "  ✗ conda not available"
fi

# 2. Cargo - check if package command works
echo ""
echo "→ Checking Cargo..."
if command -v cargo >/dev/null 2>&1; then
    echo "  ✓ cargo available"
    echo "  Note: cargo-local-registry install happens in test"
else
    echo "  ✗ cargo not available"
fi

# 3. GitHub CLI - check auth
echo ""
echo "→ Checking GitHub CLI..."
if command -v gh >/dev/null 2>&1; then
    if gh auth status >/dev/null 2>&1; then
        echo "  ✓ gh authenticated"
    else
        echo "  ⚠ gh installed but not authenticated (github-draft-release needs auth)"
        echo "    Run: gh auth login"
    fi
else
    echo "  ✗ gh not available"
fi

# 4. Helm - check if it can add repos
echo ""
echo "→ Checking Helm..."
if command -v helm >/dev/null 2>&1; then
    echo "  ✓ helm available"
    echo "  Note: helm repo add might fail in sandboxed env (expected)"
else
    echo "  ✗ helm not available"
fi

# 5. npm - check if Docker can run verdaccio
echo ""
echo "→ Checking npm/verdaccio..."
if command -v docker >/dev/null 2>&1; then
    echo "  ✓ Docker available for verdaccio"
    echo "  Note: verdaccio test might skip if port conflicts"
else
    echo "  ✗ Docker not available"
fi

# 6. RubyGems - check gem command
echo ""
echo "→ Checking RubyGems..."
if command -v gem >/dev/null 2>&1; then
    echo "  ✓ gem available"
    if ! gem list -i rubygems-generate_index >/dev/null 2>&1; then
        echo "  Installing rubygems-generate_index..."
        gem install rubygems-generate_index 2>&1 | grep -v "WARNING" || true
    else
        echo "  ✓ rubygems-generate_index installed"
    fi
else
    echo "  ✗ gem not available"
fi

# 7. Terraform - check init
echo ""
echo "→ Checking Terraform..."
if command -v terraform >/dev/null 2>&1; then
    echo "  ✓ terraform available"
    echo "  Note: terraform init might fail without network or valid config"
else
    echo "  ✗ terraform not available"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "  Diagnosis complete! Run Phase 1 tests to see improvements:"
echo "  ./scripts/phase1-testing/run-all.sh"
echo "═══════════════════════════════════════════════════════════════════"
