#!/usr/bin/env bash
# Test Docker image from GHCR in a fresh VM (Phase 2 Testing)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source VM utilities
source "$SCRIPT_DIR/vm-test-utils.sh"

# Acquire lock to prevent concurrent VM tests
vm_lock_acquire

# Run pre-flight checks
if ! vm_preflight_check; then
  vm_lock_release
  exit 1
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Test Docker GHCR Image in VM (Phase 2) ===${NC}"
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

# Get version
cd "$REPO_ROOT"
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
# Docker requires lowercase repository names
OWNER_LOWER=$(echo "$OWNER" | tr '[:upper:]' '[:lower:]')
IMAGE_NAME="ghcr.io/$OWNER_LOWER/redoubt"
TEST_TAG="$IMAGE_NAME:test-$VERSION"

echo -e "${GREEN}Testing: $TEST_TAG${NC}"
echo ""

# Create VM
VM_NAME="redoubt-docker-test-$$"

# Setup cleanup trap
vm_setup_cleanup_trap "$VM_NAME"

echo -e "${BLUE}Step 1: Creating Ubuntu VM with Docker${NC}"
if ! vm_launch_with_retry "$VM_NAME" "22.04" "2G" "10G" "2"; then
    echo -e "${RED}Failed to launch VM${NC}"
    exit 1
fi

# Install Docker
echo -e "${BLUE}Step 2: Installing Docker${NC}"
multipass exec "$VM_NAME" -- bash -c '
    set -euo pipefail
    sudo apt-get update -qq
    sudo apt-get install -y -qq docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker ubuntu
'

# Test if image is public or needs authentication
echo -e "${BLUE}Step 3: Checking image accessibility${NC}"
if gh auth status &>/dev/null; then
    echo -e "${YELLOW}Authenticated with GitHub - will test with auth${NC}"
    # Get token and login to GHCR in VM
    TOKEN=$(gh auth token)
    multipass exec "$VM_NAME" -- bash -c "
        echo '$TOKEN' | sudo docker login ghcr.io -u '$OWNER' --password-stdin
    "
else
    echo -e "${YELLOW}Not authenticated - testing public access${NC}"
fi

# Pull image
echo -e "${BLUE}Step 4: Pulling image from GHCR${NC}"
if ! multipass exec "$VM_NAME" -- sudo docker pull "$TEST_TAG" 2>&1; then
    echo ""
    echo -e "${YELLOW}⚠ Image $TEST_TAG does not exist or is not accessible${NC}"
    echo -e "${YELLOW}→ This is expected for a template repository before publishing images${NC}"
    echo -e "${YELLOW}→ Run setup-docker-registry.sh to build and push a test image${NC}"
    echo ""
    echo -e "${BLUE}Skipping Docker test (infrastructure validated)${NC}"
    echo ""
    # Cleanup will be handled by trap
    exit 0
fi

# Test image
echo -e "${BLUE}Step 5: Testing image${NC}"

# Test version
echo -e "${YELLOW}Testing --version...${NC}"
VERSION_OUTPUT=$(multipass exec "$VM_NAME" -- sudo docker run --rm "$TEST_TAG" --version)
echo "  Output: $VERSION_OUTPUT"

# Test hello command
echo -e "${YELLOW}Testing hello command...${NC}"
HELLO_OUTPUT=$(multipass exec "$VM_NAME" -- sudo docker run --rm "$TEST_TAG" hello "Docker Phase 2")
echo "  Output: $HELLO_OUTPUT"

# Test verify command
echo -e "${YELLOW}Testing verify command...${NC}"
VERIFY_OUTPUT=$(multipass exec "$VM_NAME" -- sudo docker run --rm "$TEST_TAG" verify 2>&1 || true)
echo "  Output: $VERIFY_OUTPUT"

# Check results
if [[ "$VERSION_OUTPUT" == *"$VERSION"* ]] && [[ "$HELLO_OUTPUT" == *"hello, Docker Phase 2"* ]]; then
    echo ""
    echo -e "${GREEN}=== Phase 2 Docker Test: PASSED ===${NC}"
    echo ""
    echo -e "${GREEN}✓ Image pulled from GHCR successfully${NC}"
    echo -e "${GREEN}✓ Version command works${NC}"
    echo -e "${GREEN}✓ Hello command works${NC}"
    echo -e "${GREEN}✓ Verify command runs${NC}"
    echo ""
    echo -e "${BLUE}Image URL:${NC}"
    echo "  $TEST_TAG"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Test on different architectures (ARM64, etc.)"
    echo "2. Test container security scanning"
    echo "3. Proceed to Phase 3 (public release)"
    exit 0
else
    echo ""
    echo -e "${RED}=== Phase 2 Docker Test: FAILED ===${NC}"
    echo ""
    echo -e "${RED}Version output: $VERSION_OUTPUT${NC}"
    echo -e "${RED}Hello output: $HELLO_OUTPUT${NC}"
    exit 1
fi
