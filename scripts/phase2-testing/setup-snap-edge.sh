#!/usr/bin/env bash
# Setup Snap edge channel for Phase 2 Testing

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}"))" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Snap Edge Channel Setup (Phase 2 Testing) ===${NC}"
echo ""

# Check for snapcraft
if ! command -v snapcraft &> /dev/null; then
    echo -e "${RED}Error: snapcraft not installed${NC}"
    echo "Install with: sudo snap install snapcraft --classic"
    exit 1
fi

# Check snapcraft login
echo -e "${BLUE}Step 1: Check Snapcraft authentication${NC}"
if ! snapcraft whoami &>/dev/null; then
    echo -e "${YELLOW}Not logged in to Snapcraft${NC}"
    echo "Run: snapcraft login"
    echo ""
    echo "You'll need:"
    echo "- A Snapcraft account (https://snapcraft.io)"
    echo "- Your app registered: snapcraft register provenance-demo"
    exit 1
fi
echo -e "${GREEN}✓ Logged in to Snapcraft${NC}"
echo ""

# Build snap
echo -e "${BLUE}Step 2: Building snap${NC}"
cd "$REPO_ROOT"

# First build the .pyz
./scripts/build_pyz.sh

# Build snap
snapcraft clean
snapcraft

echo -e "${GREEN}✓ Snap built${NC}"
echo ""

# Upload to edge channel
echo -e "${BLUE}Step 3: Uploading to edge channel${NC}"
SNAP_FILE=$(ls *.snap | head -n1)

if [ -z "$SNAP_FILE" ]; then
    echo -e "${RED}Error: No .snap file found${NC}"
    exit 1
fi

echo "Uploading $SNAP_FILE to edge channel..."
snapcraft upload "$SNAP_FILE" --release edge

echo -e "${GREEN}✓ Uploaded to edge channel${NC}"
echo ""

# Test locally first
echo -e "${BLUE}Step 4: Testing local snap${NC}"
sudo snap install "$SNAP_FILE" --dangerous

echo "Testing version..."
provenance-demo.redoubt --version

echo "Testing hello..."
provenance-demo.redoubt hello "Snap Edge"

sudo snap remove provenance-demo

echo -e "${GREEN}✓ Local test passed${NC}"
echo ""

# Instructions
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
echo -e "${YELLOW}Phase 2 Testing Instructions:${NC}"
echo ""
echo "1. Install from edge channel:"
echo -e "   ${BLUE}sudo snap install provenance-demo --edge${NC}"
echo ""
echo "2. Test the snap:"
echo -e "   ${BLUE}provenance-demo.redoubt --version${NC}"
echo -e "   ${BLUE}provenance-demo.redoubt hello world${NC}"
echo -e "   ${BLUE}provenance-demo.redoubt verify${NC}"
echo ""
echo "3. Test in a fresh VM:"
echo -e "   ${BLUE}./scripts/phase2-testing/test-snap-edge-vm.sh${NC}"
echo ""
echo -e "${BLUE}Snap Store URL:${NC}"
echo "   https://snapcraft.io/provenance-demo"
echo ""
echo -e "${YELLOW}Note:${NC} Edge channel updates take ~5 minutes to propagate"
echo ""
echo -e "${GREEN}Happy testing! 📦${NC}"
