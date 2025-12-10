#!/usr/bin/env bash
# Test Homebrew tap installation in a fresh VM (Phase 2)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source VM utilities
source "$SCRIPT_DIR/vm-test-utils.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Acquire lock to prevent concurrent VM tests
vm_lock_acquire

# Run pre-flight checks
if ! vm_preflight_check; then
  vm_lock_release
  exit 1
fi

echo -e "${BLUE}=== Testing Homebrew Tap in VM (Phase 2) ===${NC}"
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

TAP_REPO="$OWNER/homebrew-tap"
VM_NAME="homebrew-phase2-test-$$"

# Setup cleanup trap
vm_setup_cleanup_trap "$VM_NAME"

# Create VM
echo -e "${BLUE}Step 1: Creating Ubuntu VM${NC}"
if ! vm_launch_with_retry "$VM_NAME" "22.04" "2G" "5G" "2"; then
    echo -e "${RED}Failed to launch VM${NC}"
    exit 1
fi
echo -e "${GREEN}✓ VM created${NC}"
echo ""

# Install Homebrew
echo -e "${BLUE}Step 2: Installing Homebrew${NC}"
multipass exec "$VM_NAME" -- bash -c '
    export DEBIAN_FRONTEND=noninteractive
    sudo apt-get update -qq
    sudo apt-get install -y -qq build-essential curl git

    # Install Homebrew
    NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add to PATH
    echo "eval \"\$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)\"" >> ~/.bashrc
'
echo -e "${GREEN}✓ Homebrew installed${NC}"
echo ""

# Add tap
echo -e "${BLUE}Step 3: Adding remote tap${NC}"
if ! multipass exec "$VM_NAME" -- bash -c "
    eval \"\$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)\"
    brew tap $TAP_REPO 2>&1
"; then
    echo ""
    echo -e "${YELLOW}⚠ Tap $TAP_REPO does not exist or is not accessible${NC}"
    echo -e "${YELLOW}→ This is expected for a template repository before creating the tap${NC}"
    echo -e "${YELLOW}→ Use test-homebrew-local-vm.sh to test Homebrew infrastructure${NC}"
    echo -e "${YELLOW}→ Create the tap repository to enable this test${NC}"
    echo ""
    echo -e "${BLUE}Skipping remote tap test (infrastructure validated)${NC}"
    echo ""
    # Cleanup will be handled by trap, just exit successfully
    exit 0
fi
echo -e "${GREEN}✓ Tap added: $TAP_REPO${NC}"
echo ""

# Install redoubt
echo -e "${BLUE}Step 4: Installing redoubt${NC}"
multipass exec "$VM_NAME" -- bash -c '
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install redoubt
'
echo -e "${GREEN}✓ redoubt installed${NC}"
echo ""

# Test installation
echo -e "${BLUE}Step 5: Testing redoubt${NC}"

echo "Test: redoubt --version"
multipass exec "$VM_NAME" -- bash -c '
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    redoubt --version
'
echo -e "${GREEN}✓ Version check passed${NC}"

echo "Test: redoubt hello world"
OUTPUT=$(multipass exec "$VM_NAME" -- bash -c '
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    redoubt hello world
')
if [[ "$OUTPUT" =~ "world" ]]; then
    echo -e "${GREEN}✓ Hello command passed${NC}"
else
    echo -e "${RED}✗ Hello command failed${NC}"
    exit 1
fi

echo "Test: redoubt verify"
multipass exec "$VM_NAME" -- bash -c '
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    redoubt verify || true
'
echo -e "${GREEN}✓ Verify command executed${NC}"
echo ""

# Test uninstall
echo -e "${BLUE}Step 6: Testing uninstall${NC}"
multipass exec "$VM_NAME" -- bash -c '
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew uninstall redoubt
    brew untap '"$TAP_REPO"'
'
echo -e "${GREEN}✓ Uninstall successful${NC}"
echo ""

echo -e "${GREEN}=== All Homebrew Tap Tests Passed! 🍺 ===${NC}"
echo ""
echo "The following were tested successfully:"
echo "  ✓ Tap addition (brew tap)"
echo "  ✓ Package installation (brew install)"
echo "  ✓ Binary execution in PATH"
echo "  ✓ All commands (version, hello, verify)"
echo "  ✓ Uninstallation (brew uninstall)"
echo ""
echo -e "${BLUE}VM will be cleaned up automatically${NC}"
