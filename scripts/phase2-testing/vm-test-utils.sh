#!/usr/bin/env bash
# Shared utilities for VM-based testing
# Ensures sequential execution and proper cleanup

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# Lock directory location (using directory for cross-platform atomicity)
VM_LOCK_DIR="${VM_LOCK_DIR:-/tmp/redoubt-vm-tests.lock.d}"
VM_LOCK_PID_FILE="$VM_LOCK_DIR/pid"
VM_LOCK_MAX_AGE=3600  # Consider lock stale after 1 hour

# Acquire exclusive lock for VM tests
# This prevents multiple VM tests from running concurrently
# Uses directory creation which is atomic on both Linux and macOS
vm_lock_acquire() {
    local timeout=${1:-300}  # Default 5 minute timeout
    local waited=0

    echo -e "${BLUE}→ Acquiring VM test lock...${NC}"

    # Try to acquire lock with timeout
    while true; do
        # Try to create lock directory (atomic operation)
        if mkdir "$VM_LOCK_DIR" 2>/dev/null; then
            # Successfully acquired lock
            echo "$$" > "$VM_LOCK_PID_FILE"
            echo -e "${GREEN}✓ VM test lock acquired${NC}"
            return 0
        fi

        # Check if lock is stale
        if [ -d "$VM_LOCK_DIR" ]; then
            local lock_age=0
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS stat syntax
                lock_age=$(( $(date +%s) - $(stat -f %m "$VM_LOCK_DIR" 2>/dev/null || echo 0) ))
            else
                # Linux stat syntax
                lock_age=$(( $(date +%s) - $(stat -c %Y "$VM_LOCK_DIR" 2>/dev/null || echo 0) ))
            fi

            if [ $lock_age -gt $VM_LOCK_MAX_AGE ]; then
                echo -e "${YELLOW}⚠ Lock appears stale (${lock_age}s old), removing...${NC}"
                vm_lock_release
                continue
            fi

            # Check if the process holding the lock still exists
            if [ -f "$VM_LOCK_PID_FILE" ]; then
                local lock_pid=$(cat "$VM_LOCK_PID_FILE" 2>/dev/null || echo "")
                if [ -n "$lock_pid" ] && ! ps -p "$lock_pid" > /dev/null 2>&1; then
                    echo -e "${YELLOW}⚠ Lock holder (PID $lock_pid) no longer running, removing stale lock...${NC}"
                    vm_lock_release
                    continue
                fi
            fi
        fi

        # Check timeout
        if [ $waited -ge $timeout ]; then
            echo -e "${RED}✗ Failed to acquire VM test lock after ${timeout}s${NC}"
            echo -e "${YELLOW}Another VM test may be running. Check with: ps aux | grep -E 'test.*vm\\.sh'${NC}"
            if [ -f "$VM_LOCK_PID_FILE" ]; then
                local lock_pid=$(cat "$VM_LOCK_PID_FILE" 2>/dev/null || echo "unknown")
                echo -e "${YELLOW}Lock held by PID: $lock_pid${NC}"
            fi
            echo -e "${YELLOW}To manually remove stale lock: rm -rf $VM_LOCK_DIR${NC}"
            return 1
        fi

        if [ $((waited % 10)) -eq 0 ]; then
            echo -e "${YELLOW}⏳ Waiting for other VM tests to complete... (${waited}s)${NC}"
        fi

        sleep 2
        waited=$((waited + 2))
    done
}

# Release VM test lock
vm_lock_release() {
    if [ -d "$VM_LOCK_DIR" ]; then
        echo -e "${BLUE}→ Releasing VM test lock...${NC}"
        rm -rf "$VM_LOCK_DIR" 2>/dev/null || true
        echo -e "${GREEN}✓ VM test lock released${NC}"
    fi
}

# Clean up a specific VM
vm_cleanup() {
    local vm_name=$1

    if ! multipass list 2>/dev/null | grep -q "^$vm_name"; then
        return 0
    fi

    echo -e "${YELLOW}→ Cleaning up VM: $vm_name${NC}"

    # Try to stop first
    if multipass list 2>/dev/null | grep "^$vm_name" | grep -q "Running"; then
        if ! multipass stop "$vm_name" 2>/dev/null; then
            echo -e "${YELLOW}⚠ Failed to stop VM gracefully, forcing...${NC}"
        fi
        sleep 2
    fi

    # Delete the VM
    if ! multipass delete "$vm_name" 2>/dev/null; then
        echo -e "${RED}✗ Failed to delete VM: $vm_name${NC}"
        echo -e "${YELLOW}You may need to manually clean up with: multipass delete -p $vm_name${NC}"
        return 1
    fi

    # Purge immediately
    if ! multipass purge 2>/dev/null; then
        echo -e "${YELLOW}⚠ Failed to purge deleted VMs${NC}"
        return 1
    fi

    echo -e "${GREEN}✓ VM cleaned up: $vm_name${NC}"
    return 0
}

# Clean up all test VMs (those matching test- prefix or redoubt- prefix)
vm_cleanup_all_test_vms() {
    echo -e "${BLUE}→ Cleaning up all test VMs...${NC}"

    local cleaned=0
    local failed=0

    # Get list of VMs matching test patterns
    while IFS= read -r vm_name; do
        if [[ -n "$vm_name" ]]; then
            if vm_cleanup "$vm_name"; then
                cleaned=$((cleaned + 1))
            else
                failed=$((failed + 1))
            fi
        fi
    done < <(multipass list 2>/dev/null | awk 'NR>1 {print $1}' | grep -E '^(test-|redoubt-)' || true)

    if [ $cleaned -gt 0 ]; then
        echo -e "${GREEN}✓ Cleaned up $cleaned test VM(s)${NC}"
    else
        echo -e "${GREEN}✓ No test VMs to clean up${NC}"
    fi

    if [ $failed -gt 0 ]; then
        echo -e "${RED}✗ Failed to clean up $failed VM(s)${NC}"
        return 1
    fi

    return 0
}

# Pre-flight check before running VM tests
vm_preflight_check() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${BLUE}VM Test Pre-flight Check${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

    # Check if multipass is installed
    if ! command -v multipass >/dev/null 2>&1; then
        echo -e "${RED}✗ multipass is not installed${NC}"
        echo -e "${YELLOW}Install it with: brew install --cask multipass${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ multipass is installed${NC}"

    # Check if multipass is running
    if ! multipass version >/dev/null 2>&1; then
        echo -e "${RED}✗ multipass is not running${NC}"
        echo -e "${YELLOW}Start it with: sudo launchctl start com.canonical.multipassd${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ multipass is running${NC}"

    # Check for lingering test VMs
    local lingering_count=$(multipass list 2>/dev/null | awk 'NR>1 {print $1}' | grep -E '^(test-|redoubt-)' | wc -l | tr -d ' ')
    lingering_count=${lingering_count:-0}  # Default to 0 if empty
    if [ "$lingering_count" -gt 0 ] 2>/dev/null; then
        echo -e "${YELLOW}⚠ Found $lingering_count lingering test VM(s)${NC}"
        echo -e "${YELLOW}→ Cleaning up before proceeding...${NC}"
        if ! vm_cleanup_all_test_vms; then
            echo -e "${RED}✗ Failed to clean up lingering VMs${NC}"
            return 1
        fi
    else
        echo -e "${GREEN}✓ No lingering test VMs${NC}"
    fi

    # Check available disk space (warn if < 10GB)
    local available_space
    if [[ "$OSTYPE" == "darwin"* ]]; then
        available_space=$(df -g / | awk 'NR==2 {print $4}')
        if [ "$available_space" -lt 10 ]; then
            echo -e "${YELLOW}⚠ Low disk space: ${available_space}GB available${NC}"
            echo -e "${YELLOW}  VM tests may fail with less than 10GB free${NC}"
        else
            echo -e "${GREEN}✓ Sufficient disk space: ${available_space}GB available${NC}"
        fi
    else
        available_space=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
        if [ "$available_space" -lt 10 ]; then
            echo -e "${YELLOW}⚠ Low disk space: ${available_space}GB available${NC}"
            echo -e "${YELLOW}  VM tests may fail with less than 10GB free${NC}"
        else
            echo -e "${GREEN}✓ Sufficient disk space: ${available_space}GB available${NC}"
        fi
    fi

    echo -e "${GREEN}✓ Pre-flight check passed${NC}"
    echo ""
    return 0
}

# Setup trap for cleanup on exit
vm_setup_cleanup_trap() {
    local vm_name=$1

    # Define cleanup function for this specific VM
    eval "cleanup_${vm_name//-/_}() {
        echo \"\"
        echo -e \"${YELLOW}→ Running cleanup for VM: $vm_name${NC}\"
        vm_cleanup \"$vm_name\"
        vm_lock_release
    }"

    # Set trap
    trap "cleanup_${vm_name//-/_}" EXIT INT TERM
}

# Launch a VM with retries and proper error handling
vm_launch_with_retry() {
    local vm_name=$1
    local image=$2
    local memory=${3:-2G}
    local disk=${4:-10G}
    local cpus=${5:-2}
    local max_retries=${6:-3}

    echo -e "${BLUE}→ Launching VM: $vm_name (image: $image)${NC}"

    local attempt=1
    while [ $attempt -le $max_retries ]; do
        if multipass launch "$image" --name "$vm_name" --memory "$memory" --disk "$disk" --cpus "$cpus" --timeout 300; then
            echo -e "${GREEN}✓ VM launched successfully: $vm_name${NC}"

            # Wait for VM to stabilize
            echo -e "${BLUE}→ Waiting for VM to stabilize...${NC}"
            sleep 10

            # Verify VM is running
            if multipass list | grep "^$vm_name" | grep -q "Running"; then
                echo -e "${GREEN}✓ VM is running and ready${NC}"
                return 0
            else
                echo -e "${RED}✗ VM launched but not running properly${NC}"
            fi
        fi

        if [ $attempt -lt $max_retries ]; then
            echo -e "${YELLOW}⚠ Launch failed (attempt $attempt/$max_retries), retrying...${NC}"
            vm_cleanup "$vm_name"
            sleep 10
            attempt=$((attempt + 1))
        else
            echo -e "${RED}✗ Failed to launch VM after $max_retries attempts${NC}"
            return 1
        fi
    done

    return 1
}

# Export functions for use in scripts
export -f vm_lock_acquire
export -f vm_lock_release
export -f vm_cleanup
export -f vm_cleanup_all_test_vms
export -f vm_preflight_check
export -f vm_setup_cleanup_trap
export -f vm_launch_with_retry
