#!/bin/bash
# Test release creation script
# This creates an alpha pre-release to test the release automation

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default version
VERSION="${1:-v0.0.1-alpha.1}"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   Test Release Creation${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${YELLOW}Version: ${VERSION}${NC}"
echo ""

# Check if tag already exists
if git rev-parse "$VERSION" >/dev/null 2>&1; then
    echo -e "${RED}Error: Tag $VERSION already exists${NC}"
    echo ""
    echo "To delete existing tag:"
    echo "  git tag -d $VERSION"
    echo "  git push --delete origin $VERSION"
    exit 1
fi

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) not found${NC}"
    echo ""
    echo "Install with: brew install gh"
    echo "Then login: gh auth login"
    exit 1
fi

# Confirm
echo -e "${YELLOW}This will:${NC}"
echo "  1. Create git tag: $VERSION"
echo "  2. Push tag to GitHub"
echo "  3. Create pre-release on GitHub"
echo "  4. Trigger release workflows"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Aborted${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Step 1: Creating and pushing tag...${NC}"
git tag "$VERSION"
git push origin "$VERSION"
echo -e "${GREEN}✓ Tag created and pushed${NC}"

echo ""
echo -e "${BLUE}Step 2: Creating GitHub pre-release...${NC}"
gh release create "$VERSION" \
  --title "$VERSION - Test Release" \
  --notes "🧪 **Test Release**

This is a pre-release for testing the release automation pipeline.

**What's being tested:**
- ✅ PyPI/TestPyPI publishing
- ✅ Docker GHCR multi-arch builds
- ✅ Homebrew formula updates
- ✅ Nix/Cachix builds
- ✅ SBOM generation
- ✅ Attestations

**Installation (TestPyPI):**
\`\`\`bash
pip install --index-url https://test.pypi.org/simple/ \\
    --extra-index-url https://pypi.org/simple/ \\
    provenance-demo
\`\`\`

**Docker:**
\`\`\`bash
docker pull ghcr.io/hollowsunhc/provenance-demo:${VERSION#v}
\`\`\`

---
🤖 Generated with test-release.sh" \
  --prerelease

echo -e "${GREEN}✓ Pre-release created${NC}"

echo ""
echo -e "${BLUE}Step 3: Monitoring workflows...${NC}"
echo ""
gh run list --limit 10

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}   Test Release Created!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${YELLOW}Monitor workflows at:${NC}"
echo "  https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/actions"
echo ""
echo -e "${YELLOW}View release at:${NC}"
echo "  https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/releases/tag/$VERSION"
echo ""
echo -e "${YELLOW}When done testing, cleanup with:${NC}"
echo "  gh release delete $VERSION --yes"
echo "  git push --delete origin $VERSION"
echo "  git tag -d $VERSION"
echo ""
echo -e "${BLUE}Tip: Watch workflows in real-time:${NC}"
echo "  gh run watch"
echo ""
