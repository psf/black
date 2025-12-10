#!/usr/bin/env bash
# Setup private RPM repository for Phase 2 Testing

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}"))" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== RPM Private Repository Setup (Phase 2 Testing) ===${NC}"
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

if ! command -v rpmbuild &> /dev/null; then
    MISSING_TOOLS+=("rpmbuild (install: brew install rpm or apt-get install rpm)")
fi

if ! command -v createrepo_c &> /dev/null && ! command -v createrepo &> /dev/null; then
    MISSING_TOOLS+=("createrepo (install: brew install createrepo_c or apt-get install createrepo-c)")
fi

if ! command -v gh &> /dev/null; then
    MISSING_TOOLS+=("gh (GitHub CLI)")
fi

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo -e "${RED}Error: Missing required tools:${NC}"
    for tool in "${MISSING_TOOLS[@]}"; do
        echo "  - $tool"
    done
    echo ""
    echo -e "${YELLOW}On macOS:${NC}"
    echo "  brew install rpm createrepo_c"
    echo ""
    echo -e "${YELLOW}On Fedora/RHEL:${NC}"
    echo "  sudo dnf install rpm-build createrepo_c"
    echo ""
    echo -e "${YELLOW}On Ubuntu/Debian:${NC}"
    echo "  sudo apt-get install rpm createrepo-c"
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

# Build .rpm package
echo -e "${BLUE}Step 4: Building .rpm package${NC}"

# Create RPM build structure
RPM_DIR="$REPO_ROOT/build/rpm"
rm -rf "$RPM_DIR"
mkdir -p "$RPM_DIR"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Copy binary to SOURCES
cp "$BINARY_PATH" "$RPM_DIR/SOURCES/"

# Create spec file
cat > "$RPM_DIR/SPECS/redoubt.spec" <<EOF
Name:           redoubt
Version:        $VERSION
Release:        1%{?dist}
Summary:        Self-verifying CLI demonstrating reproducible, attestable releases

License:        MIT
URL:            https://github.com/$OWNER/$REPO
Source0:        provenance-demo.pyz

BuildArch:      noarch
Requires:       python3 >= 3.10

%description
Redoubt is a self-verifying CLI tool that demonstrates complete supply chain
security with reproducible builds, SLSA provenance, SBOM generation, and
Sigstore attestations.

%prep
# No prep needed for single file

%build
# No build needed for .pyz

%install
rm -rf \$RPM_BUILD_ROOT
mkdir -p \$RPM_BUILD_ROOT/usr/bin
install -m 755 %{SOURCE0} \$RPM_BUILD_ROOT/usr/bin/redoubt

%files
%defattr(-,root,root,-)
/usr/bin/redoubt

%changelog
* $(date "+%a %b %d %Y") $OWNER <noreply@github.com> - $VERSION-1
- Initial package release
EOF

# Build RPM
rpmbuild --define "_topdir $RPM_DIR" -ba "$RPM_DIR/SPECS/redoubt.spec"

# Find the built RPM
RPM_FILE=$(find "$RPM_DIR/RPMS" -name "*.rpm" -type f | head -n1)
if [ ! -f "$RPM_FILE" ]; then
    echo -e "${RED}Error: Failed to build .rpm package${NC}"
    exit 1
fi

echo -e "${GREEN}✓ .rpm package built: $(basename "$RPM_FILE")${NC}"
echo ""

# Create RPM repository on GitHub
echo -e "${BLUE}Step 5: Setting up RPM repository on GitHub Pages${NC}"

RPM_REPO="$OWNER/rpm-repo"

if ! gh repo view "$RPM_REPO" &>/dev/null; then
    echo "Creating $RPM_REPO..."
    gh repo create "$RPM_REPO" --public --description "RPM repository for $OWNER packages"
else
    echo -e "${GREEN}✓ RPM repository already exists${NC}"
fi

# Clone and setup
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"
gh repo clone "$RPM_REPO"
cd rpm-repo

# Enable GitHub Pages if not already enabled
gh api -X POST "repos/$RPM_REPO/pages" \
    -f source[branch]=main \
    -f source[path]=/ \
    2>/dev/null || echo "GitHub Pages may already be enabled"

# Create repository structure
mkdir -p packages

# Copy RPM to packages
cp "$RPM_FILE" packages/

# Create repository metadata
if command -v createrepo_c &> /dev/null; then
    createrepo_c packages/
else
    createrepo packages/
fi

# Create repo file
cat > redoubt.repo <<EOF
[redoubt]
name=Redoubt RPM Repository
baseurl=https://$OWNER.github.io/rpm-repo/packages
enabled=1
gpgcheck=0
EOF

# Create installation script
cat > install.sh <<'EOF'
#!/bin/bash
set -e

OWNER="OWNER_PLACEHOLDER"
REPO_URL="https://${OWNER}.github.io/rpm-repo"

echo "Adding RPM repository..."

# Add repository
sudo curl -fsSL "$REPO_URL/redoubt.repo" -o /etc/yum.repos.d/redoubt.repo

# Install
if command -v dnf &> /dev/null; then
    sudo dnf install -y redoubt
else
    sudo yum install -y redoubt
fi

echo "Installation complete!"
echo "Run: redoubt --version"
EOF

sed -i.bak "s/OWNER_PLACEHOLDER/$OWNER/g" install.sh && rm install.sh.bak
chmod +x install.sh

# Create README
cat > README.md <<EOF
# RPM Repository

RPM repository for $OWNER packages.

## Installation

### Quick Install (Fedora/RHEL/CentOS)

\`\`\`bash
curl -fsSL https://$OWNER.github.io/rpm-repo/install.sh | bash
\`\`\`

### Manual Install

\`\`\`bash
# Add repository
sudo curl -fsSL https://$OWNER.github.io/rpm-repo/redoubt.repo -o /etc/yum.repos.d/redoubt.repo

# Install (Fedora/RHEL 8+)
sudo dnf install redoubt

# Or (RHEL 7/CentOS 7)
sudo yum install redoubt
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
git commit -m "Add redoubt $VERSION to RPM repository" || true
git push

echo -e "${GREEN}✓ RPM repository updated${NC}"
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
echo "1. Quick install (Fedora/RHEL/CentOS):"
echo -e "   ${BLUE}curl -fsSL https://$OWNER.github.io/rpm-repo/install.sh | bash${NC}"
echo ""
echo "2. Manual install:"
echo -e "   ${BLUE}sudo curl -fsSL https://$OWNER.github.io/rpm-repo/redoubt.repo -o /etc/yum.repos.d/redoubt.repo${NC}"
echo -e "   ${BLUE}sudo dnf install redoubt${NC}  # or 'sudo yum install redoubt'"
echo ""
echo "3. Test the installation:"
echo -e "   ${BLUE}redoubt --version${NC}"
echo -e "   ${BLUE}redoubt hello world${NC}"
echo -e "   ${BLUE}redoubt verify${NC}"
echo ""
echo "4. Test in a VM:"
echo -e "   ${BLUE}./scripts/phase2-testing/test-rpm-repo-vm.sh${NC}"
echo ""
echo -e "${BLUE}Repository URL:${NC}"
echo "   https://$OWNER.github.io/rpm-repo"
echo ""
echo -e "${YELLOW}Note:${NC} gpgcheck=0 for testing. For production, sign RPMs with GPG."
echo ""
echo -e "${GREEN}Happy testing! 📦${NC}"
