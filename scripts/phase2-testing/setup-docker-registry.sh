#!/usr/bin/env bash
# Setup and test Docker with GitHub Container Registry (Phase 2 Testing)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Docker + GHCR Setup (Phase 2 Testing) ===${NC}"
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker not installed${NC}"
    exit 1
fi

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

# Check GitHub CLI authentication
echo -e "${BLUE}Step 1: Check GitHub authentication${NC}"
if ! gh auth status &>/dev/null; then
    echo -e "${YELLOW}Not authenticated with GitHub CLI${NC}"
    echo "Run: gh auth login"
    exit 1
fi
echo -e "${GREEN}✓ GitHub CLI authenticated${NC}"
echo ""

# Login to GHCR
echo -e "${BLUE}Step 2: Login to GitHub Container Registry${NC}"
gh auth token | docker login ghcr.io -u "$OWNER" --password-stdin
echo -e "${GREEN}✓ Logged in to GHCR${NC}"
echo ""

# Build Docker image
echo -e "${BLUE}Step 3: Building Docker image${NC}"
cd "$REPO_ROOT"

VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
IMAGE_NAME="ghcr.io/$OWNER/redoubt"
TEST_TAG="$IMAGE_NAME:test-$VERSION"
LATEST_TAG="$IMAGE_NAME:test-latest"

docker build -t "$TEST_TAG" -t "$LATEST_TAG" .
echo -e "${GREEN}✓ Image built: $TEST_TAG${NC}"
echo ""

# Test locally first
echo -e "${BLUE}Step 4: Testing image locally${NC}"
docker run "$TEST_TAG" --version
docker run "$TEST_TAG" hello "Docker Phase 2"
echo -e "${GREEN}✓ Local tests passed${NC}"
echo ""

# Push to GHCR
echo -e "${BLUE}Step 5: Pushing to GHCR${NC}"
docker push "$TEST_TAG"
docker push "$LATEST_TAG"
echo -e "${GREEN}✓ Pushed to GHCR${NC}"
echo ""

# Test pull from registry
echo -e "${BLUE}Step 6: Testing pull from registry${NC}"
docker rmi "$TEST_TAG" || true
docker pull "$TEST_TAG"
docker run "$TEST_TAG" --version
echo -e "${GREEN}✓ Pull and run successful${NC}"
echo ""

# Instructions
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
echo -e "${YELLOW}Phase 2 Testing Instructions:${NC}"
echo ""
echo "1. Anyone with access can pull and test:"
echo -e "   ${BLUE}docker pull $TEST_TAG${NC}"
echo -e "   ${BLUE}docker run $TEST_TAG hello world${NC}"
echo -e "   ${BLUE}docker run $TEST_TAG verify${NC}"
echo ""
echo "2. Test in a fresh environment:"
echo -e "   ${BLUE}./scripts/phase2-testing/test-docker-registry-vm.sh${NC}"
echo ""
echo -e "${BLUE}GitHub Container Registry URL:${NC}"
echo "   https://github.com/$OWNER/$REPO/pkgs/container/redoubt"
echo ""
echo -e "${YELLOW}Note:${NC} Make sure the package visibility is set correctly:"
echo "   - Public: Anyone can pull"
echo "   - Private: Only you and collaborators can pull"
echo ""
echo -e "${GREEN}Happy testing! 🐳${NC}"
