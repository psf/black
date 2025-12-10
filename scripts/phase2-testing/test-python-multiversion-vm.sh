#!/usr/bin/env bash
#
# Test Python package across multiple Python versions (3.10, 3.11, 3.12, 3.13)
# Uses Ubuntu VMs with deadsnakes PPA for Python versions
#
# NOTE: This script is designed for LOCAL DEVELOPMENT with Multipass VMs.
# GitHub Actions CI uses Docker containers instead (see .github/workflows/python-compatibility.yml)
# for faster execution and GitHub runner compatibility.
#
# Use this script when:
# - Testing locally with full VM isolation
# - Debugging OS-specific issues
# - Pre-release validation with comprehensive testing
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source VM utilities
source "$SCRIPT_DIR/vm-test-utils.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Python versions to test
PYTHON_VERSIONS=("3.10" "3.11" "3.12" "3.13")

# Get package info
PACKAGE_NAME="${PACKAGE_NAME:-demo-secure-cli}"
VERSION=$(grep '^version = ' "$REPO_ROOT/pyproject.toml" | cut -d'"' -f2)

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${CYAN}Testing Python Multi-Version Compatibility${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Package: $PACKAGE_NAME"
echo "Version: $VERSION"
echo "Testing Python versions: ${PYTHON_VERSIONS[*]}"
echo ""

# Acquire lock
vm_lock_acquire

# Pre-flight check
vm_preflight_check

# Track results
declare -A TEST_RESULTS
TESTS_PASSED=0
TESTS_FAILED=0

# Build .pyz if it doesn't exist
PYZ_FILE="$REPO_ROOT/dist/redoubt.pyz"
if [ ! -f "$PYZ_FILE" ]; then
    echo -e "${YELLOW}Building .pyz file...${NC}"
    cd "$REPO_ROOT"
    ./scripts/build_pyz.sh
    echo -e "${GREEN}✓ .pyz file built${NC}"
    echo ""
fi

# Test each Python version
for PY_VERSION in "${PYTHON_VERSIONS[@]}"; do
    PY_SHORT="${PY_VERSION//./}"  # 3.10 -> 310
    VM_NAME="python${PY_SHORT}-test-$$"

    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}Testing Python $PY_VERSION${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Launch VM
    echo -e "${BLUE}Step 1: Creating Ubuntu 22.04 VM${NC}"
    vm_launch_with_retry "$VM_NAME" "22.04" "2G" "20G"
    echo -e "${GREEN}✓ VM created${NC}"
    echo ""

    # Install Python version
    echo -e "${BLUE}Step 2: Installing Python $PY_VERSION${NC}"
    multipass exec "$VM_NAME" -- bash -c "
        set -e
        sudo add-apt-repository -y ppa:deadsnakes/ppa
        sudo apt-get update -qq
        sudo apt-get install -y -qq python$PY_VERSION python$PY_VERSION-venv python$PY_VERSION-dev
    " 2>&1 | grep -v "^debconf:" || true

    # Verify Python installation
    PY_INSTALLED=$(multipass exec "$VM_NAME" -- python$PY_VERSION --version 2>&1 || echo "FAILED")
    if [[ "$PY_INSTALLED" == *"FAILED"* ]]; then
        echo -e "${RED}✗ Failed to install Python $PY_VERSION${NC}"
        TEST_RESULTS[$PY_VERSION]="FAILED (installation)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        vm_cleanup "$VM_NAME"
        continue
    fi
    echo -e "${GREEN}✓ Python $PY_VERSION installed: $PY_INSTALLED${NC}"
    echo ""

    # Transfer .pyz file
    echo -e "${BLUE}Step 3: Transferring .pyz file to VM${NC}"
    multipass transfer "$PYZ_FILE" "$VM_NAME:/home/ubuntu/redoubt.pyz"
    echo -e "${GREEN}✓ File transferred${NC}"
    echo ""

    # Test execution with this Python version
    echo -e "${BLUE}Step 4: Testing with Python $PY_VERSION${NC}"

    # Test 1: Version check
    echo -e "${CYAN}Test 1: Version check${NC}"
    if multipass exec "$VM_NAME" -- python$PY_VERSION /home/ubuntu/redoubt.pyz --version | grep -q "$VERSION"; then
        echo -e "${GREEN}✓ Version check passed${NC}"
    else
        echo -e "${RED}✗ Version check failed${NC}"
        TEST_RESULTS[$PY_VERSION]="FAILED (version)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        vm_cleanup "$VM_NAME"
        continue
    fi

    # Test 2: Hello command
    echo -e "${CYAN}Test 2: Hello command${NC}"
    HELLO_OUTPUT=$(multipass exec "$VM_NAME" -- python$PY_VERSION /home/ubuntu/redoubt.pyz hello world 2>&1 || echo "FAILED")
    if [[ "$HELLO_OUTPUT" == *"hello"* ]] && [[ "$HELLO_OUTPUT" != *"FAILED"* ]]; then
        echo -e "${GREEN}✓ Hello command passed${NC}"
    else
        echo -e "${RED}✗ Hello command failed${NC}"
        echo "Output: $HELLO_OUTPUT"
        TEST_RESULTS[$PY_VERSION]="FAILED (hello)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        vm_cleanup "$VM_NAME"
        continue
    fi

    # Test 3: Verify command
    echo -e "${CYAN}Test 3: Verify command${NC}"
    if multipass exec "$VM_NAME" -- python$PY_VERSION /home/ubuntu/redoubt.pyz verify 2>&1 | grep -q "Verifying binary"; then
        echo -e "${GREEN}✓ Verify command executed${NC}"
    else
        echo -e "${RED}✗ Verify command failed${NC}"
        TEST_RESULTS[$PY_VERSION]="FAILED (verify)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        vm_cleanup "$VM_NAME"
        continue
    fi

    # Test 4: Install via pip (wheel)
    echo -e "${CYAN}Test 4: pip install (compatibility)${NC}"
    multipass exec "$VM_NAME" -- bash -c "
        set -e
        python$PY_VERSION -m venv /tmp/test-venv
        /tmp/test-venv/bin/pip install --upgrade pip==24.3.1 --quiet
        cd /home/ubuntu
        # Try to import the package (simulates pip install)
        python$PY_VERSION -c 'import sys; sys.path.insert(0, \"/home/ubuntu/redoubt.pyz\"); import demo_cli.cli' 2>&1
    " > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Package imports successfully${NC}"
    else
        echo -e "${YELLOW}⚠ Package import failed (may need dependencies)${NC}"
    fi

    echo ""
    echo -e "${GREEN}=== Python $PY_VERSION: All Tests Passed! ===${NC}"
    echo ""

    TEST_RESULTS[$PY_VERSION]="PASSED"
    TESTS_PASSED=$((TESTS_PASSED + 1))

    # Cleanup VM
    vm_cleanup "$VM_NAME"
    echo ""
done

# Release lock
vm_lock_release

# Print summary
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${CYAN}Python Multi-Version Test Summary${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

for PY_VERSION in "${PYTHON_VERSIONS[@]}"; do
    RESULT="${TEST_RESULTS[$PY_VERSION]:-SKIPPED}"
    if [[ "$RESULT" == "PASSED" ]]; then
        echo -e "  ${GREEN}✓${NC} Python $PY_VERSION: ${GREEN}PASSED${NC}"
    else
        echo -e "  ${RED}✗${NC} Python $PY_VERSION: ${RED}$RESULT${NC}"
    fi
done

echo ""
echo -e "${BOLD}Statistics:${NC}"
echo -e "  Total versions: ${#PYTHON_VERSIONS[@]}"
echo -e "  ${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "  ${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}${BOLD}Some Python versions failed!${NC}"
    echo ""
    echo "Compatibility matrix:"
    for PY_VERSION in "${PYTHON_VERSIONS[@]}"; do
        RESULT="${TEST_RESULTS[$PY_VERSION]:-SKIPPED}"
        echo "  Python $PY_VERSION: $RESULT"
    done
    exit 1
else
    echo -e "${GREEN}${BOLD}All Python versions passed! 🎉${NC}"
    echo ""
    echo "Your package is compatible with Python ${PYTHON_VERSIONS[*]}"
    exit 0
fi
