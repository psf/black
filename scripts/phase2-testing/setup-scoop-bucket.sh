#!/usr/bin/env bash
# Setup private Scoop bucket for Phase 2 Testing

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}"))" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Scoop Private Bucket Setup (Phase 2 Testing) ===${NC}"
echo ""

# Get GitHub info
CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
if [[ "$CURRENT_REMOTE" =~ github.com[:/]([^/]+)/([^/.]+) ]]; then
    OWNER="${BASH_REMATCH[1]}"
    REPO="${BASH_REMATCH[2]}"
else
    echo -e "${RED}Error: Could not parse GitHub owner/repo${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Detected GitHub: $OWNER/$REPO${NC}"
echo ""

# Check GitHub CLI
echo -e "${BLUE}Step 1: Check GitHub authentication${NC}"
if ! gh auth status &>/dev/null; then
    echo -e "${YELLOW}Not authenticated with GitHub CLI${NC}"
    echo "Run: gh auth login"
    exit 1
fi
echo -e "${GREEN}✓ GitHub CLI authenticated${NC}"
echo ""

# Create scoop-bucket repo if it doesn't exist
BUCKET_REPO="$OWNER/scoop-bucket"
echo -e "${BLUE}Step 2: Setup Scoop bucket repository${NC}"

if ! gh repo view "$BUCKET_REPO" &>/dev/null; then
    echo "Creating $BUCKET_REPO..."
    gh repo create "$BUCKET_REPO" --public --description "Scoop bucket for $OWNER packages"

    # Clone and initialize
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    git clone "https://github.com/$BUCKET_REPO.git"
    cd scoop-bucket

    # Create bucket directory
    mkdir -p bucket

    # Create README
    cat > README.md <<EOF
# Scoop Bucket

Scoop bucket for $OWNER packages.

## Installation

\`\`\`powershell
scoop bucket add $OWNER https://github.com/$BUCKET_REPO
\`\`\`

## Available Packages

- \`redoubt\` - Self-verifying CLI demonstrating reproducible, attestable releases
EOF

    git add .
    git commit -m "Initialize Scoop bucket"
    git push

    cd "$REPO_ROOT"
    rm -rf "$TEMP_DIR"
else
    echo -e "${GREEN}✓ Bucket repository already exists${NC}"
fi
echo ""

# Build the binary
echo -e "${BLUE}Step 3: Building provenance-demo.pyz${NC}"
cd "$REPO_ROOT"
./scripts/build_pyz.sh

BINARY_PATH="dist/provenance-demo.pyz"
if [ ! -f "$BINARY_PATH" ]; then
    echo -e "${RED}Error: $BINARY_PATH not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Binary built${NC}"
echo ""

# Get version
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
TEST_TAG="test-v$VERSION"

# Create test release in main repo
echo -e "${BLUE}Step 4: Creating test release${NC}"

# Delete existing test release if it exists
gh release delete "$TEST_TAG" --repo "$OWNER/$REPO" --yes 2>/dev/null || true

# Create new test release
gh release create "$TEST_TAG" \
    --repo "$OWNER/$REPO" \
    --title "Test Release $VERSION (Scoop Testing)" \
    --notes "Test release for Phase 2 Scoop bucket testing. Do not use in production." \
    --prerelease \
    "$BINARY_PATH"

echo -e "${GREEN}✓ Test release created${NC}"
echo ""

# Calculate SHA256
echo -e "${BLUE}Step 5: Calculating SHA256${NC}"
BINARY_SHA256=$(shasum -a 256 "$BINARY_PATH" | cut -d' ' -f1)
echo "SHA256: $BINARY_SHA256"
echo ""

# Update Scoop manifest
echo -e "${BLUE}Step 6: Updating Scoop manifest${NC}"

# Clone bucket repo
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"
gh repo clone "$BUCKET_REPO"
cd scoop-bucket

# Ensure bucket directory exists
mkdir -p bucket

# Create manifest
DOWNLOAD_URL="https://github.com/$OWNER/$REPO/releases/download/$TEST_TAG/provenance-demo.pyz"

cat > bucket/redoubt.json <<EOF
{
    "version": "$VERSION",
    "description": "Self-verifying CLI demonstrating reproducible, attestable releases with full supply chain security",
    "homepage": "https://github.com/$OWNER/$REPO",
    "license": "MIT",
    "url": "$DOWNLOAD_URL",
    "hash": "$BINARY_SHA256",
    "bin": "provenance-demo.pyz",
    "pre_install": [
        "if (!(Test-Path \"\$env:USERPROFILE\\.redoubt\")) { New-Item -ItemType Directory -Path \"\$env:USERPROFILE\\.redoubt\" -Force | Out-Null }"
    ],
    "checkver": {
        "url": "https://api.github.com/repos/$OWNER/$REPO/releases/latest",
        "jsonpath": "\$.tag_name",
        "regex": "v([\\d.]+)"
    },
    "autoupdate": {
        "url": "https://github.com/$OWNER/$REPO/releases/download/v\$version/provenance-demo.pyz"
    },
    "notes": [
        "Run 'redoubt --version' to verify installation",
        "Run 'redoubt hello world' to test",
        "Run 'redoubt verify' to verify attestations"
    ]
}
EOF

# Commit and push
git add bucket/redoubt.json
git commit -m "Update redoubt to $VERSION (test release)"
git push

echo -e "${GREEN}✓ Manifest updated${NC}"
echo ""

# Cleanup
cd "$REPO_ROOT"
rm -rf "$TEMP_DIR"

# Instructions
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
echo -e "${YELLOW}Phase 2 Testing Instructions:${NC}"
echo ""
echo -e "${BLUE}Windows (PowerShell):${NC}"
echo ""
echo "1. Add the bucket:"
echo -e "   ${BLUE}scoop bucket add $OWNER https://github.com/$BUCKET_REPO${NC}"
echo ""
echo "2. Install redoubt:"
echo -e "   ${BLUE}scoop install redoubt${NC}"
echo ""
echo "3. Test the installation:"
echo -e "   ${BLUE}redoubt --version${NC}"
echo -e "   ${BLUE}redoubt hello world${NC}"
echo -e "   ${BLUE}redoubt verify${NC}"
echo ""
echo "4. Update to new versions:"
echo -e "   ${BLUE}scoop update redoubt${NC}"
echo ""
echo -e "${BLUE}Test in Windows VM:${NC}"
echo "   Note: Requires Windows VM with Scoop installed"
echo "   (Manual testing required - no automated script for Windows VMs yet)"
echo ""
echo -e "${BLUE}Bucket URL:${NC}"
echo "   https://github.com/$BUCKET_REPO"
echo ""
echo -e "${YELLOW}Note:${NC} This uses a test release (prerelease). For production, use official releases."
echo ""
echo -e "${GREEN}Happy testing! 🪣${NC}"
