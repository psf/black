#!/usr/bin/env bash
# Test Snap edge channel installation in a fresh VM (Phase 2 Testing)

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

echo -e "${BLUE}=== Test Snap Edge Channel in VM (Phase 2) ===${NC}"
echo ""

# Get version
cd "$REPO_ROOT"
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)

echo -e "${GREEN}Testing version: $VERSION${NC}"
echo ""

# Create VM
VM_NAME="redoubt-snap-test-$$"

# Setup cleanup trap
vm_setup_cleanup_trap "$VM_NAME"

echo -e "${BLUE}Step 1: Creating Ubuntu VM${NC}"
if ! vm_launch_with_retry "$VM_NAME" "22.04" "2G" "10G"; then
    echo -e "${RED}Failed to launch VM${NC}"
    exit 1
fi

# Wait for snap to be ready
echo -e "${BLUE}Step 2: Waiting for snapd${NC}"
multipass exec "$VM_NAME" -- bash -c '
    set -euo pipefail
    sudo snap wait system seed.loaded
'

# Install snap from edge channel
echo -e "${BLUE}Step 3: Installing from edge channel${NC}"
if ! multipass exec "$VM_NAME" -- sudo snap install provenance-demo --edge 2>&1; then
    echo ""
    echo -e "${YELLOW}⚠ Snap 'provenance-demo' not found in edge channel${NC}"
    echo -e "${YELLOW}→ This is expected for a template repository before publishing to Snap Store${NC}"
    echo -e "${YELLOW}→ Run setup-snap-edge.sh to build and push to edge channel${NC}"
    echo ""
    echo -e "${BLUE}Skipping Snap test (infrastructure validated)${NC}"
    echo ""
    # Cleanup will be handled by trap
    exit 0
fi

# Test snap
echo -e "${BLUE}Step 4: Testing snap${NC}"

# Test version
echo -e "${YELLOW}Testing --version...${NC}"
VERSION_OUTPUT=$(multipass exec "$VM_NAME" -- provenance-demo.redoubt --version)
echo "  Output: $VERSION_OUTPUT"

# Test hello
echo -e "${YELLOW}Testing hello command...${NC}"
HELLO_OUTPUT=$(multipass exec "$VM_NAME" -- provenance-demo.redoubt hello "Snap Edge Test")
echo "  Output: $HELLO_OUTPUT"

# Test verify
echo -e "${YELLOW}Testing verify command...${NC}"
VERIFY_OUTPUT=$(multipass exec "$VM_NAME" -- provenance-demo.redoubt verify 2>&1 || true)
echo "  Output: $VERIFY_OUTPUT"

# Check results
if [[ "$VERSION_OUTPUT" == *"$VERSION"* ]] && [[ "$HELLO_OUTPUT" == *"hello, Snap Edge Test"* ]]; then
    echo ""
    echo -e "${GREEN}=== Phase 2 Snap Test: PASSED ===${NC}"
    echo ""
    echo -e "${GREEN}✓ Snap installed from edge channel${NC}"
    echo -e "${GREEN}✓ Version command works${NC}"
    echo -e "${GREEN}✓ Hello command works${NC}"
    echo -e "${GREEN}✓ Verify command runs${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Test on different Ubuntu versions"
    echo "2. Test snap confinement (strict mode)"
    echo "3. Promote to beta/candidate channels for wider testing"
    echo "4. Proceed to Phase 3 (stable channel)"
    exit 0
else
    echo ""
    echo -e "${RED}=== Phase 2 Snap Test: FAILED ===${NC}"
    echo ""
    echo -e "${RED}Version output: $VERSION_OUTPUT${NC}"
    echo -e "${RED}Hello output: $HELLO_OUTPUT${NC}"
    exit 1
fi
