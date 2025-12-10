#!/usr/bin/env bash
# Cleanup utility for orphaned VM test instances
# Can be run manually or scheduled as a cron job

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source utilities
source "$SCRIPT_DIR/vm-test-utils.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Clean up orphaned VM test instances"
    echo ""
    echo "Options:"
    echo "  --all           Clean up ALL VMs (not just test VMs)"
    echo "  --force         Don't ask for confirmation"
    echo "  --list-only     Only list VMs, don't clean up"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Clean up test VMs with confirmation"
    echo "  $0 --force            # Clean up test VMs without confirmation"
    echo "  $0 --list-only        # Just show what would be cleaned"
    echo "  $0 --all --force      # Clean up ALL VMs (dangerous!)"
}

# Parse arguments
CLEAN_ALL=false
FORCE=false
LIST_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            CLEAN_ALL=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --list-only)
            LIST_ONLY=true
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
done

echo -e "${BOLD}${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${BLUE}║              VM Test Cleanup Utility                               ║${NC}"
echo -e "${BOLD}${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if multipass is available
if ! command -v multipass >/dev/null 2>&1; then
    echo -e "${RED}✗ multipass is not installed${NC}"
    exit 1
fi

# Get list of VMs
echo -e "${BLUE}→ Scanning for VMs...${NC}"
echo ""

if [ "$CLEAN_ALL" = true ]; then
    VM_LIST=$(multipass list 2>/dev/null | awk 'NR>1 {print $1}' || true)
    PATTERN="all VMs"
else
    VM_LIST=$(multipass list 2>/dev/null | awk 'NR>1 {print $1}' | grep -E '^(test-|redoubt-)' || true)
    PATTERN="test VMs (test-*, redoubt-*)"
fi

if [ -z "$VM_LIST" ]; then
    echo -e "${GREEN}✓ No VMs found to clean up${NC}"
    exit 0
fi

# Count VMs
VM_COUNT=$(echo "$VM_LIST" | wc -l | tr -d ' ')

echo -e "${YELLOW}Found $VM_COUNT VM(s) matching pattern: $PATTERN${NC}"
echo ""
echo -e "${BOLD}VMs to be cleaned:${NC}"

# Show detailed list
while IFS= read -r vm_name; do
    if [[ -n "$vm_name" ]]; then
        vm_info=$(multipass list 2>/dev/null | grep "^$vm_name" || echo "$vm_name Unknown Unknown")
        state=$(echo "$vm_info" | awk '{print $2}')
        ipv4=$(echo "$vm_info" | awk '{print $3}')

        if [[ "$state" == "Running" ]]; then
            echo -e "  ${YELLOW}▶${NC} $vm_name (${GREEN}$state${NC}, $ipv4)"
        elif [[ "$state" == "Stopped" ]]; then
            echo -e "  ${BLUE}■${NC} $vm_name (${BLUE}$state${NC})"
        else
            echo -e "  ${RED}●${NC} $vm_name ($state)"
        fi
    fi
done <<< "$VM_LIST"

echo ""

# Exit if list-only mode
if [ "$LIST_ONLY" = true ]; then
    echo -e "${BLUE}List-only mode: no cleanup performed${NC}"
    exit 0
fi

# Confirm unless --force
if [ "$FORCE" = false ]; then
    echo -e "${YELLOW}${BOLD}WARNING:${NC} This will delete the VMs listed above."
    echo -n "Are you sure you want to continue? [y/N] "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Cleanup cancelled${NC}"
        exit 0
    fi
    echo ""
fi

# Perform cleanup
echo -e "${BLUE}→ Starting cleanup...${NC}"
echo ""

CLEANED=0
FAILED=0

while IFS= read -r vm_name; do
    if [[ -n "$vm_name" ]]; then
        echo -e "${BLUE}Cleaning up: $vm_name${NC}"

        # Stop if running
        if multipass list 2>/dev/null | grep "^$vm_name" | grep -q "Running"; then
            echo -e "  ${YELLOW}→ Stopping...${NC}"
            if ! multipass stop "$vm_name" 2>/dev/null; then
                echo -e "  ${YELLOW}⚠ Failed to stop gracefully${NC}"
            fi
            sleep 2
        fi

        # Delete
        echo -e "  ${BLUE}→ Deleting...${NC}"
        if multipass delete "$vm_name" 2>/dev/null; then
            CLEANED=$((CLEANED + 1))
            echo -e "  ${GREEN}✓ Deleted${NC}"
        else
            FAILED=$((FAILED + 1))
            echo -e "  ${RED}✗ Failed to delete${NC}"
        fi
        echo ""
    fi
done <<< "$VM_LIST"

# Purge all deleted VMs
echo -e "${BLUE}→ Purging deleted VMs...${NC}"
if multipass purge 2>/dev/null; then
    echo -e "${GREEN}✓ Purged successfully${NC}"
else
    echo -e "${YELLOW}⚠ Failed to purge (this is usually not critical)${NC}"
fi

echo ""
echo -e "${BOLD}${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${BLUE}║                     Cleanup Summary                                ║${NC}"
echo -e "${BOLD}${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Total VMs found:  ${BOLD}$VM_COUNT${NC}"
echo -e "  ${GREEN}Cleaned:${NC}          ${GREEN}$CLEANED${NC}"
echo -e "  ${RED}Failed:${NC}           ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}${BOLD}Some VMs failed to clean up${NC}"
    echo -e "${YELLOW}Try running with sudo or check multipass logs${NC}"
    exit 1
else
    echo -e "${GREEN}${BOLD}✓ Cleanup completed successfully${NC}"
    exit 0
fi
