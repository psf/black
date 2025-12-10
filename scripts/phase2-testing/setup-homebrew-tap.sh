#!/usr/bin/env bash
# Setup and test Homebrew private tap (Phase 2 Testing)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Homebrew Private Tap Setup (Phase 2 Testing) ===${NC}"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Get current GitHub info
CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
if [[ -z "$CURRENT_REMOTE" ]]; then
    echo -e "${RED}Error: No git remote 'origin' found${NC}"
    exit 1
fi

# Extract owner and repo from remote URL
if [[ "$CURRENT_REMOTE" =~ github.com[:/]([^/]+)/([^/.]+) ]]; then
    OWNER="${BASH_REMATCH[1]}"
    REPO="${BASH_REMATCH[2]}"
else
    echo -e "${RED}Error: Could not parse GitHub owner/repo from: $CURRENT_REMOTE${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Detected GitHub: $OWNER/$REPO${NC}"
echo ""

# Check if homebrew-tap repo exists
TAP_REPO="$OWNER/homebrew-tap"
echo -e "${BLUE}Step 1: Check if tap repository exists${NC}"
echo "Checking: https://github.com/$TAP_REPO"

if gh repo view "$TAP_REPO" &>/dev/null; then
    echo -e "${GREEN}✓ Repository $TAP_REPO already exists${NC}"
else
    echo -e "${YELLOW}! Repository $TAP_REPO does not exist${NC}"
    read -p "Create it now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Creating repository..."
        gh repo create "$TAP_REPO" --public --description "Homebrew tap for $REPO" --confirm
        echo -e "${GREEN}✓ Created repository: $TAP_REPO${NC}"
    else
        echo -e "${RED}Error: Tap repository required for testing${NC}"
        exit 1
    fi
fi
echo ""

# Clone or update tap repository
TAP_DIR="$HOME/.homebrew-tap-test"
echo -e "${BLUE}Step 2: Clone/update tap repository${NC}"

if [[ -d "$TAP_DIR" ]]; then
    echo "Updating existing clone at: $TAP_DIR"
    cd "$TAP_DIR"
    git pull
else
    echo "Cloning to: $TAP_DIR"
    git clone "https://github.com/$TAP_REPO.git" "$TAP_DIR"
    cd "$TAP_DIR"
fi

echo -e "${GREEN}✓ Tap repository ready${NC}"
echo ""

# Create Formula directory if it doesn't exist
echo -e "${BLUE}Step 3: Setup Formula directory${NC}"
mkdir -p Formula
echo -e "${GREEN}✓ Formula directory ready${NC}"
echo ""

# Build the binary
echo -e "${BLUE}Step 4: Build binary${NC}"
cd "$REPO_ROOT"
./scripts/build_pyz.sh
BINARY_PATH="$REPO_ROOT/dist/provenance-demo.pyz"

if [[ ! -f "$BINARY_PATH" ]]; then
    echo -e "${RED}Error: Binary not found at: $BINARY_PATH${NC}"
    exit 1
fi

# Calculate SHA256
BINARY_SHA256=$(shasum -a 256 "$BINARY_PATH" | awk '{print $1}')
echo -e "${GREEN}✓ Binary built${NC}"
echo "   SHA256: $BINARY_SHA256"
echo ""

# Create a temporary GitHub release for testing
echo -e "${BLUE}Step 5: Create test release${NC}"
VERSION=$(grep '^version = ' "$REPO_ROOT/pyproject.toml" | cut -d'"' -f2)
TEST_TAG="v${VERSION}-test"

echo "Creating test release: $TEST_TAG"

# Delete existing test release if it exists
if gh release view "$TEST_TAG" &>/dev/null; then
    echo "Deleting existing test release..."
    gh release delete "$TEST_TAG" --yes --cleanup-tag 2>/dev/null || true
fi

# Create new test release
gh release create "$TEST_TAG" \
    --repo "$OWNER/$REPO" \
    --title "Test Release $VERSION" \
    --notes "**This is a test release for Phase 2 testing. Not for production use.**" \
    --prerelease \
    "$BINARY_PATH"

DOWNLOAD_URL="https://github.com/$OWNER/$REPO/releases/download/$TEST_TAG/provenance-demo.pyz"
echo -e "${GREEN}✓ Test release created${NC}"
echo "   URL: $DOWNLOAD_URL"
echo ""

# Update Formula
echo -e "${BLUE}Step 6: Update Homebrew formula${NC}"
cd "$TAP_DIR"

cat > Formula/redoubt.rb <<EOF
# Homebrew Formula for Redoubt Release Demo
# This is a TEST formula for Phase 2 testing

class Redoubt < Formula
  desc "Self-verifying CLI demonstrating reproducible, attestable releases"
  homepage "https://github.com/$OWNER/$REPO"
  url "$DOWNLOAD_URL"
  sha256 "$BINARY_SHA256"
  license "MIT"

  depends_on "python@3.10"

  def install
    bin.install "provenance-demo.pyz" => "redoubt"
  end

  test do
    system "#{bin}/redoubt", "--version"
    system "#{bin}/redoubt", "hello", "world"
  end
end
EOF

echo -e "${GREEN}✓ Formula updated${NC}"
echo ""

# Commit and push
echo -e "${BLUE}Step 7: Commit and push formula${NC}"
git add Formula/redoubt.rb
git commit -m "Update redoubt formula for test release $TEST_TAG" || echo "No changes to commit"
git push

echo -e "${GREEN}✓ Formula pushed to GitHub${NC}"
echo ""

# Instructions for testing
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
echo -e "${YELLOW}Phase 2 Testing Instructions:${NC}"
echo ""
echo "1. In a VM or clean environment, run:"
echo -e "   ${BLUE}brew tap $TAP_REPO${NC}"
echo -e "   ${BLUE}brew install redoubt${NC}"
echo ""
echo "2. Test the installation:"
echo -e "   ${BLUE}redoubt --version${NC}"
echo -e "   ${BLUE}redoubt hello world${NC}"
echo -e "   ${BLUE}redoubt verify${NC}"
echo ""
echo "3. Test uninstallation:"
echo -e "   ${BLUE}brew uninstall redoubt${NC}"
echo -e "   ${BLUE}brew untap $TAP_REPO${NC}"
echo ""
echo -e "${YELLOW}Automated VM Test:${NC}"
echo -e "   ${BLUE}./scripts/phase2-testing/test-homebrew-tap-vm.sh${NC}"
echo ""
echo -e "${GREEN}Happy testing! 🍺${NC}"
