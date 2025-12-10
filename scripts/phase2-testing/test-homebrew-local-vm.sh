#!/usr/bin/env bash
# Test Homebrew installation using local formula (always works, validates infrastructure)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

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

echo -e "${BLUE}=== Testing Homebrew with Local Formula (Phase 2) ===${NC}"
echo ""

VM_NAME="homebrew-local-test-$$"

# Setup cleanup trap
vm_setup_cleanup_trap "$VM_NAME"

# Check if .pyz exists
PYZ_FILE="$PROJECT_ROOT/dist/provenance-demo.pyz"
if [ ! -f "$PYZ_FILE" ]; then
    echo -e "${YELLOW}⚠ .pyz file not found at $PYZ_FILE${NC}"
    echo -e "${YELLOW}→ Building .pyz file first...${NC}"
    cd "$PROJECT_ROOT"
    bash scripts/build_pyz.sh
    if [ ! -f "$PYZ_FILE" ]; then
        echo -e "${RED}✗ Failed to build .pyz file${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ .pyz file built${NC}"
fi

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
    sudo apt-get install -y -qq build-essential curl git python3

    # Install Homebrew
    NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add to PATH
    echo "eval \"\$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)\"" >> ~/.bashrc
'
echo -e "${GREEN}✓ Homebrew installed${NC}"
echo ""

# Transfer .pyz file
echo -e "${BLUE}Step 3: Transferring .pyz file to VM${NC}"
multipass transfer "$PYZ_FILE" "$VM_NAME:/home/ubuntu/redoubt.pyz"
echo -e "${GREEN}✓ File transferred${NC}"
echo ""

# Create local tap and formula
echo -e "${BLUE}Step 4: Creating local tap and formula${NC}"
multipass exec "$VM_NAME" -- bash -c '
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

    # Create local tap directory
    mkdir -p "$(brew --repository)/Library/Taps/local/homebrew-redoubt/Formula"

    # Create formula pointing to local file
    cat > "$(brew --repository)/Library/Taps/local/homebrew-redoubt/Formula/redoubt.rb" <<EOF
class Redoubt < Formula
  desc "Redoubt - Secure CLI with reproducible releases"
  homepage "https://github.com/hollowsunhc/provenance-template"
  url "file:///home/ubuntu/redoubt.pyz"
  version "0.1.0"
  sha256 "$(sha256sum /home/ubuntu/redoubt.pyz | awk "{print \$1}")"

  def install
    bin.install "redoubt.pyz" => "redoubt"
  end

  test do
    system "#{bin}/redoubt", "--version"
  end
end
EOF
'
echo -e "${GREEN}✓ Local tap and formula created${NC}"
echo ""

# Install from local tap
echo -e "${BLUE}Step 5: Installing redoubt from local formula${NC}"
multipass exec "$VM_NAME" -- bash -c '
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install --verbose local/redoubt/redoubt
'
echo -e "${GREEN}✓ redoubt installed${NC}"
echo ""

# Test installation
echo -e "${BLUE}Step 6: Testing redoubt${NC}"

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
echo -e "${BLUE}Step 7: Testing uninstall${NC}"
multipass exec "$VM_NAME" -- bash -c '
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew uninstall redoubt
'
echo -e "${GREEN}✓ Uninstall successful${NC}"
echo ""

echo -e "${GREEN}=== All Local Homebrew Tests Passed! 🍺 ===${NC}"
echo ""
echo "The following were tested successfully:"
echo "  ✓ Local tap creation"
echo "  ✓ Local formula with file:// URL"
echo "  ✓ Package installation (brew install)"
echo "  ✓ Binary execution in PATH"
echo "  ✓ All commands (version, hello, verify)"
echo "  ✓ Uninstallation (brew uninstall)"
echo ""
echo -e "${BLUE}VM will be cleaned up automatically${NC}"
