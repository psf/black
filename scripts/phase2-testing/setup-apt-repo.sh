#!/usr/bin/env bash
# Setup private APT repository for Phase 2 Testing

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}"))" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== APT Private Repository Setup (Phase 2 Testing) ===${NC}"
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

# Check for required tools
echo -e "${BLUE}Step 1: Check required tools${NC}"
MISSING_TOOLS=()

if ! command -v dpkg-deb &> /dev/null; then
    MISSING_TOOLS+=("dpkg-deb (install: apt-get install dpkg-dev)")
fi

if ! command -v gh &> /dev/null; then
    MISSING_TOOLS+=("gh (GitHub CLI)")
fi

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo -e "${RED}Error: Missing required tools:${NC}"
    for tool in "${MISSING_TOOLS[@]}"; do
        echo "  - $tool"
    done
    exit 1
fi

echo -e "${GREEN}✓ All required tools installed${NC}"
echo ""

# Check GitHub authentication
echo -e "${BLUE}Step 2: Check GitHub authentication${NC}"
if ! gh auth status &>/dev/null; then
    echo -e "${YELLOW}Not authenticated with GitHub CLI${NC}"
    echo "Run: gh auth login"
    exit 1
fi
echo -e "${GREEN}✓ GitHub CLI authenticated${NC}"
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

# Build .deb package
echo -e "${BLUE}Step 4: Building .deb package${NC}"

# Create package structure
DEB_DIR="$REPO_ROOT/build/deb"
rm -rf "$DEB_DIR"
mkdir -p "$DEB_DIR/redoubt_${VERSION}_all"

# Create directory structure
mkdir -p "$DEB_DIR/redoubt_${VERSION}_all/usr/bin"
mkdir -p "$DEB_DIR/redoubt_${VERSION}_all/usr/share/doc/redoubt"
mkdir -p "$DEB_DIR/redoubt_${VERSION}_all/DEBIAN"

# Copy binary
cp "$BINARY_PATH" "$DEB_DIR/redoubt_${VERSION}_all/usr/bin/redoubt"
chmod +x "$DEB_DIR/redoubt_${VERSION}_all/usr/bin/redoubt"

# Create control file
cat > "$DEB_DIR/redoubt_${VERSION}_all/DEBIAN/control" <<EOF
Package: redoubt
Version: $VERSION
Section: utils
Priority: optional
Architecture: all
Depends: python3 (>= 3.10)
Maintainer: $OWNER
Description: Self-verifying CLI demonstrating reproducible, attestable releases
 Redoubt is a self-verifying CLI tool that demonstrates complete supply chain
 security with reproducible builds, SLSA provenance, SBOM generation, and
 Sigstore attestations.
Homepage: https://github.com/$OWNER/$REPO
EOF

# Create copyright file
cat > "$DEB_DIR/redoubt_${VERSION}_all/usr/share/doc/redoubt/copyright" <<EOF
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: redoubt
Source: https://github.com/$OWNER/$REPO

Files: *
Copyright: $(date +%Y) $OWNER
License: MIT
EOF

# Build .deb
cd "$DEB_DIR"
dpkg-deb --build "redoubt_${VERSION}_all"

DEB_FILE="$DEB_DIR/redoubt_${VERSION}_all.deb"
if [ ! -f "$DEB_FILE" ]; then
    echo -e "${RED}Error: Failed to build .deb package${NC}"
    exit 1
fi

echo -e "${GREEN}✓ .deb package built${NC}"
echo ""

# Create APT repository structure on GitHub
echo -e "${BLUE}Step 5: Setting up APT repository on GitHub Pages${NC}"

APT_REPO="$OWNER/apt-repo"

if ! gh repo view "$APT_REPO" &>/dev/null; then
    echo "Creating $APT_REPO..."
    gh repo create "$APT_REPO" --public --description "APT repository for $OWNER packages"
else
    echo -e "${GREEN}✓ APT repository already exists${NC}"
fi

# Clone and setup
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"
gh repo clone "$APT_REPO"
cd apt-repo

# Enable GitHub Pages if not already enabled
gh api -X POST "repos/$APT_REPO/pages" \
    -f source[branch]=main \
    -f source[path]=/pool \
    2>/dev/null || echo "GitHub Pages may already be enabled"

# Create repository structure
mkdir -p pool/main
mkdir -p dists/stable/main/binary-amd64
mkdir -p dists/stable/main/binary-arm64
mkdir -p dists/stable/main/binary-all

# Copy .deb to pool
cp "$DEB_FILE" pool/main/

# Generate Packages file
cd pool/main
dpkg-scanpackages . /dev/null > ../../dists/stable/main/binary-all/Packages
gzip -k -f ../../dists/stable/main/binary-all/Packages

# Generate Release file
cd ../../dists/stable
cat > Release <<EOF
Origin: $OWNER
Label: $OWNER APT Repository
Suite: stable
Codename: stable
Architectures: all amd64 arm64
Components: main
Description: APT repository for $OWNER packages
Date: $(date -R)
EOF

# Create installation script
cd ../..
cat > install.sh <<'EOF'
#!/bin/bash
set -e

OWNER="OWNER_PLACEHOLDER"
REPO_URL="https://${OWNER}.github.io/apt-repo"

echo "Adding APT repository..."

# Add repository
echo "deb [trusted=yes] $REPO_URL stable main" | sudo tee /etc/apt/sources.list.d/${OWNER}-apt-repo.list

# Update and install
sudo apt-get update
sudo apt-get install -y redoubt

echo "Installation complete!"
echo "Run: redoubt --version"
EOF

sed -i.bak "s/OWNER_PLACEHOLDER/$OWNER/g" install.sh && rm install.sh.bak
chmod +x install.sh

# Create README
cat > README.md <<EOF
# APT Repository

APT repository for $OWNER packages.

## Installation

\`\`\`bash
curl -fsSL https://$OWNER.github.io/apt-repo/install.sh | bash
\`\`\`

Or manually:

\`\`\`bash
# Add repository
echo "deb [trusted=yes] https://$OWNER.github.io/apt-repo stable main" | sudo tee /etc/apt/sources.list.d/${OWNER}-apt-repo.list

# Update and install
sudo apt-get update
sudo apt-get install redoubt
\`\`\`

## Available Packages

- \`redoubt\` - Self-verifying CLI demonstrating reproducible, attestable releases

## Verification

\`\`\`bash
redoubt --version
redoubt hello world
redoubt verify
\`\`\`
EOF

# Commit and push
git add .
git commit -m "Add redoubt $VERSION to APT repository" || true
git push

echo -e "${GREEN}✓ APT repository updated${NC}"
echo ""

# Cleanup
cd "$REPO_ROOT"
rm -rf "$TEMP_DIR"

# Wait for GitHub Pages to deploy
echo -e "${YELLOW}Waiting 30 seconds for GitHub Pages to deploy...${NC}"
sleep 30

# Instructions
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
echo -e "${YELLOW}Phase 2 Testing Instructions:${NC}"
echo ""
echo "1. Quick install (Ubuntu/Debian):"
echo -e "   ${BLUE}curl -fsSL https://$OWNER.github.io/apt-repo/install.sh | bash${NC}"
echo ""
echo "2. Manual install:"
echo -e "   ${BLUE}echo 'deb [trusted=yes] https://$OWNER.github.io/apt-repo stable main' | sudo tee /etc/apt/sources.list.d/${OWNER}-apt-repo.list${NC}"
echo -e "   ${BLUE}sudo apt-get update${NC}"
echo -e "   ${BLUE}sudo apt-get install redoubt${NC}"
echo ""
echo "3. Test the installation:"
echo -e "   ${BLUE}redoubt --version${NC}"
echo -e "   ${BLUE}redoubt hello world${NC}"
echo -e "   ${BLUE}redoubt verify${NC}"
echo ""
echo "4. Test in a VM:"
echo -e "   ${BLUE}./scripts/phase2-testing/test-apt-repo-vm.sh${NC}"
echo ""
echo -e "${BLUE}Repository URL:${NC}"
echo "   https://$OWNER.github.io/apt-repo"
echo ""
echo -e "${YELLOW}Note:${NC} Uses [trusted=yes] for testing. For production, sign with GPG."
echo ""
echo -e "${GREEN}Happy testing! 📦${NC}"
