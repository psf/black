#!/usr/bin/env bash
# Quick setup - configures what we can automatically (non-interactive)
# For full interactive setup, use setup_local_config.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Quick Setup - Auto-configuration${NC}"
echo ""

# Make all scripts executable
echo "Making scripts executable..."
chmod +x scripts/*.sh
echo -e "${GREEN}✓ Scripts are executable${NC}"

# Create distribution directories
echo ""
echo "Creating distribution directories..."
mkdir -p packaging/homebrew-tap/Formula
mkdir -p snap
echo -e "${GREEN}✓ Directories created${NC}"

# Create .env.example if it doesn't exist
if [ ! -f .env.example ]; then
    echo ""
    echo "Creating .env.example..."
    cat > .env.example <<'EOF'
# Example environment configuration
# Copy to .env and customize (DO NOT commit .env)

# GitHub Configuration
GITHUB_REPO=hollowsunhc/provenance-demo

# Optional: Homebrew Tap
HOMEBREW_TAP=OWNER/tap

# Optional: PyPI Package Name
PYPI_PACKAGE=your-package-name

# GitHub Tokens (DO NOT commit actual tokens)
# TAP_PUSH_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# WINGET_GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# PYPI_TOKEN=pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EOF
    echo -e "${GREEN}✓ Created .env.example${NC}"
fi

# Install pre-commit hooks if pre-commit is available
if command -v pre-commit &> /dev/null; then
    echo ""
    echo "Installing pre-commit hooks..."
    pre-commit install >/dev/null 2>&1 || true
    echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
else
    echo ""
    echo -e "${YELLOW}⚠  pre-commit not installed (optional)${NC}"
    echo "   Install with: pip install pre-commit"
fi

# Generate secrets baseline if detect-secrets is available
if command -v detect-secrets &> /dev/null; then
    echo ""
    echo "Generating secrets baseline..."
    detect-secrets scan > .secrets.baseline 2>/dev/null || echo "{}" > .secrets.baseline
    echo -e "${GREEN}✓ Secrets baseline created${NC}"
fi

# Build artifacts if not already built
if [ ! -f dist/provenance-demo.pyz ]; then
    echo ""
    echo "Building artifacts..."
    if [ -x scripts/build_pyz.sh ]; then
        ./scripts/build_pyz.sh
        echo -e "${GREEN}✓ Built provenance-demo.pyz${NC}"
    fi
fi

# Build wheel if python available
if command -v python3 &> /dev/null && [ ! -f dist/*.whl ]; then
    echo ""
    echo "Building wheel..."
    python3 -m pip install --quiet build==1.2.2.post1 2>/dev/null || true
    python3 -m build 2>/dev/null || true
    if ls dist/*.whl >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Built wheel and sdist${NC}"
    fi
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Quick Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo "What was configured:"
echo "  ✓ Scripts are executable"
echo "  ✓ Distribution directories created"
echo "  ✓ .env.example created"
[ -d .git/hooks ] && [ -f .git/hooks/pre-commit ] && echo "  ✓ Pre-commit hooks installed"
[ -f .secrets.baseline ] && echo "  ✓ Secrets baseline generated"
[ -f dist/provenance-demo.pyz ] && echo "  ✓ Artifacts built"
echo ""

echo "Manual configuration needed:"
echo ""
echo "1. Replace hollowsunhc/provenance-demo placeholders:"
echo "   Find: hollowsunhc/provenance-demo"
echo "   Replace with: your-org/your-repo"
echo "   Files: .github/workflows/*.yml, README.md, scripts/*.sh"
echo ""
echo "2. Update pyproject.toml:"
echo "   • name: Update package name"
echo "   • authors: Add your name/email"
echo "   • [project.scripts]: Update CLI command name"
echo ""
echo "3. Pin GitHub Action SHAs:"
echo "   Replace <PINNED_SHA> with actual commit SHAs"
echo "   See: https://github.com/OWNER/ACTION/commits/main"
echo ""
echo "For interactive setup with prompts, run:"
echo "  ./scripts/setup_local_config.sh"
echo ""
echo "To check configuration status:"
echo "  ./scripts/check_configuration.sh"
echo ""
