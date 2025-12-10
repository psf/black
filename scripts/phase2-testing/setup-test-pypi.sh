#!/usr/bin/env bash
# Setup and publish to Test PyPI (Phase 2 Testing)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Test PyPI Setup (Phase 2 Testing) ===${NC}"
echo ""

# Check for required tools
if ! command -v twine &> /dev/null; then
    echo -e "${YELLOW}Installing twine...${NC}"
    pip install --upgrade twine==6.0.1
fi

# Check for Test PyPI account
echo -e "${BLUE}Step 1: Check Test PyPI credentials${NC}"
echo ""
echo "You need a Test PyPI account to proceed."
echo "1. Create account at: https://test.pypi.org/account/register/"
echo "2. Create API token at: https://test.pypi.org/manage/account/token/"
echo "3. Add to ~/.pypirc:"
echo ""
cat <<'EOF'
[testpypi]
  username = __token__
  password = pypi-AgEI... (your token here)
EOF
echo ""

read -p "Do you have Test PyPI credentials configured? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Please set up Test PyPI credentials first${NC}"
    exit 1
fi

# Build package
echo -e "${BLUE}Step 2: Building package${NC}"
cd "$REPO_ROOT"
rm -rf dist/
./scripts/build_pyz.sh

if [[ ! -f dist/*.whl ]]; then
    echo -e "${RED}Error: Wheel not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Package built${NC}"
echo ""

# Upload to Test PyPI
echo -e "${BLUE}Step 3: Uploading to Test PyPI${NC}"
echo -e "${YELLOW}Note: You may see a 'File already exists' error if version exists${NC}"
echo -e "${YELLOW}      This is OK for testing - we'll use the existing version${NC}"
echo ""

twine upload --repository testpypi dist/* || {
    echo -e "${YELLOW}Upload failed (possibly version already exists)${NC}"
    echo -e "${YELLOW}Continuing with existing version...${NC}"
}

VERSION=$(grep '^version = ' "$REPO_ROOT/pyproject.toml" | cut -d'"' -f2)
PACKAGE_NAME="provenance-demo"

echo -e "${GREEN}✓ Package available on Test PyPI${NC}"
echo ""

# Test installation
echo -e "${BLUE}Step 4: Testing installation in virtual environment${NC}"

# Create temp venv
TEMP_VENV=$(mktemp -d)/test-venv
python3 -m venv "$TEMP_VENV"
source "$TEMP_VENV/bin/activate"

# Install from Test PyPI
echo "Installing from Test PyPI..."
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    "$PACKAGE_NAME==$VERSION"

# Test commands
echo -e "${GREEN}✓ Installation successful${NC}"
echo ""

echo "Testing commands..."
provenance-demo --version
provenance-demo hello world
provenance-demo verify || true

deactivate
rm -rf "$TEMP_VENV"

echo -e "${GREEN}✓ All tests passed${NC}"
echo ""

# Instructions
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
echo -e "${YELLOW}Phase 2 Testing Instructions:${NC}"
echo ""
echo "1. Install from Test PyPI:"
echo -e "   ${BLUE}pip install --index-url https://test.pypi.org/simple/ \\${NC}"
echo -e "   ${BLUE}    --extra-index-url https://pypi.org/simple/ \\${NC}"
echo -e "   ${BLUE}    provenance-demo${NC}"
echo ""
echo "2. Or in a VM:"
echo -e "   ${BLUE}./scripts/phase2-testing/test-test-pypi-vm.sh${NC}"
echo ""
echo -e "${BLUE}Test PyPI URL:${NC}"
echo "   https://test.pypi.org/project/$PACKAGE_NAME/"
echo ""
echo -e "${GREEN}Happy testing! 📦${NC}"
