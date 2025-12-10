#!/usr/bin/env bash
# Master test runner for all Phase 2 testing platforms
# NOTE: Each test script uses a lock mechanism to ensure sequential execution
# and proper VM cleanup. No need for additional locking here.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Test results tracking
declare -A TEST_RESULTS
declare -A TEST_TIMES
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

echo -e "${BOLD}${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${BLUE}║         Redoubt Phase 2 Testing - Master Test Runner              ║${NC}"
echo -e "${BOLD}${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Parse arguments
RUN_SETUP=false
RUN_ALL=false
PLATFORMS=()

print_usage() {
    echo "Usage: $0 [OPTIONS] [PLATFORMS]"
    echo ""
    echo "Options:"
    echo "  --setup              Run setup scripts before tests"
    echo "  --all                Run all platform tests"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Available platforms:"
    echo "  homebrew-local       Homebrew local formula (always works)"
    echo "  homebrew             Homebrew remote tap (requires tap repo)"
    echo "  pypi                 Test PyPI (Python packages)"
    echo "  python-multiversion  Test Python 3.10, 3.11, 3.12, 3.13 compatibility"
    echo "  docker               GitHub Container Registry (Docker)"
    echo "  snap                 Snap edge channel (Linux)"
    echo "  apt                  APT repository (Debian/Ubuntu)"
    echo "  rpm                  RPM repository (Fedora/RHEL)"
    echo "  appimage             AppImage build and test"
    echo "  aur                  Arch User Repository (AUR)"
    echo "  nix                  Nix with Cachix"
    echo "  flatpak              Flatpak beta channel"
    echo "  npm                  NPM GitHub Packages"
    echo "  rubygems             RubyGems GitHub Packages"
    echo "  docker-multiarch     Docker multi-architecture (ARM64 + x86_64)"
    echo ""
    echo "Examples:"
    echo "  $0 --all                    # Run all tests"
    echo "  $0 --setup homebrew docker  # Setup and test Homebrew + Docker"
    echo "  $0 pypi snap                # Test PyPI + Snap (no setup)"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --setup)
            RUN_SETUP=true
            shift
            ;;
        --all)
            RUN_ALL=true
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        homebrew-local|homebrew|pypi|python-multiversion|docker|snap|apt|rpm|appimage|aur|nix|flatpak|npm|rubygems|docker-multiarch)
            PLATFORMS+=("$1")
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
done

# If --all specified, test all platforms
if [ "$RUN_ALL" = true ]; then
    # Tests that can skip gracefully when dependencies are missing
    # Note: homebrew-local runs before homebrew to validate infrastructure first
    PLATFORMS=(
        homebrew-local
        homebrew
        pypi
        python-multiversion
        docker
        snap
        apt
        rpm
        appimage
        aur
        nix
        flatpak
        npm
        rubygems
        docker-multiarch
    )
fi

# If no platforms specified, show usage
if [ ${#PLATFORMS[@]} -eq 0 ]; then
    print_usage
    exit 1
fi

# Function to run a test with timing
run_test() {
    local platform=$1
    local test_script=$2
    local setup_script=$3

    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}Testing: $platform${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    TESTS_RUN=$((TESTS_RUN + 1))

    START_TIME=$(date +%s)

    # Run setup if requested and script exists
    if [ "$RUN_SETUP" = true ] && [ -n "$setup_script" ] && [ -f "$setup_script" ]; then
        echo -e "${YELLOW}Running setup: $setup_script${NC}"
        if ! bash "$setup_script"; then
            END_TIME=$(date +%s)
            DURATION=$((END_TIME - START_TIME))
            TEST_RESULTS[$platform]="FAILED (setup)"
            TEST_TIMES[$platform]=$DURATION
            TESTS_FAILED=$((TESTS_FAILED + 1))
            echo -e "${RED}✗ Setup failed for $platform${NC}"
            return 1
        fi
        echo ""
    fi

    # Run test
    echo -e "${YELLOW}Running test: $test_script${NC}"
    if [ ! -f "$test_script" ]; then
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        TEST_RESULTS[$platform]="SKIPPED (script not found)"
        TEST_TIMES[$platform]=$DURATION
        TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
        echo -e "${YELLOW}⊘ Test script not found: $test_script${NC}"
        return 0
    fi

    if bash "$test_script"; then
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        TEST_RESULTS[$platform]="PASSED"
        TEST_TIMES[$platform]=$DURATION
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "${GREEN}✓ $platform test passed (${DURATION}s)${NC}"
        return 0
    else
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        TEST_RESULTS[$platform]="FAILED"
        TEST_TIMES[$platform]=$DURATION
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "${RED}✗ $platform test failed${NC}"
        return 1
    fi
}

# Run tests for each platform
for platform in "${PLATFORMS[@]}"; do
    case $platform in
        homebrew-local)
            run_test "Homebrew Local Formula" \
                "$SCRIPT_DIR/test-homebrew-local-vm.sh" \
                ""
            ;;
        homebrew)
            run_test "Homebrew Remote Tap" \
                "$SCRIPT_DIR/test-homebrew-tap-vm.sh" \
                "$SCRIPT_DIR/setup-homebrew-tap.sh"
            ;;
        pypi)
            run_test "Test PyPI" \
                "$SCRIPT_DIR/test-test-pypi-vm.sh" \
                "$SCRIPT_DIR/setup-test-pypi.sh"
            ;;
        python-multiversion)
            run_test "Python Multi-Version (3.10-3.13)" \
                "$SCRIPT_DIR/test-python-multiversion-vm.sh" \
                ""
            ;;
        docker)
            run_test "Docker GHCR" \
                "$SCRIPT_DIR/test-docker-registry-vm.sh" \
                "$SCRIPT_DIR/setup-docker-registry.sh"
            ;;
        snap)
            run_test "Snap Edge" \
                "$SCRIPT_DIR/test-snap-edge-vm.sh" \
                "$SCRIPT_DIR/setup-snap-edge.sh"
            ;;
        apt)
            run_test "APT Repository" \
                "$SCRIPT_DIR/test-apt-repo-vm.sh" \
                "$SCRIPT_DIR/setup-apt-repo.sh"
            ;;
        rpm)
            run_test "RPM Repository" \
                "$SCRIPT_DIR/test-rpm-repo-vm.sh" \
                "$SCRIPT_DIR/setup-rpm-repo.sh"
            ;;
        appimage)
            run_test "AppImage" \
                "$SCRIPT_DIR/test-appimage-vm.sh" \
                "$SCRIPT_DIR/setup-appimage.sh"
            ;;
        aur)
            run_test "AUR (Arch User Repository)" \
                "$SCRIPT_DIR/test-aur-vm.sh" \
                "$SCRIPT_DIR/setup-aur.sh"
            ;;
        nix)
            run_test "Nix with Cachix" \
                "$SCRIPT_DIR/test-nix-cachix-vm.sh" \
                "$SCRIPT_DIR/nix-cachix-setup.sh"
            ;;
        flatpak)
            run_test "Flatpak Beta" \
                "$SCRIPT_DIR/test-flathub-beta-vm.sh" \
                "$SCRIPT_DIR/setup-flathub-beta.sh"
            ;;
        npm)
            run_test "NPM GitHub Packages" \
                "$SCRIPT_DIR/test-npm-github-packages-vm.sh" \
                "$SCRIPT_DIR/setup-npm-github-packages.sh"
            ;;
        rubygems)
            run_test "RubyGems GitHub Packages" \
                "$SCRIPT_DIR/test-rubygems-github-packages-vm.sh" \
                "$SCRIPT_DIR/setup-rubygems-github-packages.sh"
            ;;
        docker-multiarch)
            run_test "Docker Multi-Architecture" \
                "$SCRIPT_DIR/test-docker-multiarch.sh" \
                "$SCRIPT_DIR/setup-docker-multiarch.sh"
            ;;
    esac
done

# Print summary
echo ""
echo ""
echo -e "${BOLD}${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${BLUE}║                     Phase 2 Testing Summary                        ║${NC}"
echo -e "${BOLD}${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Print detailed results
echo -e "${BOLD}Test Results:${NC}"
echo ""
for platform in "${!TEST_RESULTS[@]}"; do
    result="${TEST_RESULTS[$platform]}"
    time="${TEST_TIMES[$platform]}"

    if [[ "$result" == "PASSED" ]]; then
        echo -e "  ${GREEN}✓${NC} ${platform}: ${GREEN}${result}${NC} (${time}s)"
    elif [[ "$result" == "SKIPPED"* ]]; then
        echo -e "  ${YELLOW}⊘${NC} ${platform}: ${YELLOW}${result}${NC} (${time}s)"
    else
        echo -e "  ${RED}✗${NC} ${platform}: ${RED}${result}${NC} (${time}s)"
    fi
done

echo ""
echo -e "${BOLD}Statistics:${NC}"
echo -e "  Total tests:    $TESTS_RUN"
echo -e "  ${GREEN}Passed:         $TESTS_PASSED${NC}"
echo -e "  ${RED}Failed:         $TESTS_FAILED${NC}"
echo -e "  ${YELLOW}Skipped:        $TESTS_SKIPPED${NC}"

echo ""

# Exit with appropriate code
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}${BOLD}Some tests failed!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Review failed test output above"
    echo "  2. Fix issues and re-run with:"
    echo "     $0 --setup <failed-platform>"
    echo "  3. Or run individual test scripts for debugging"
    exit 1
elif [ $TESTS_PASSED -eq 0 ]; then
    echo -e "${YELLOW}${BOLD}No tests passed (all skipped or failed)${NC}"
    exit 1
else
    echo -e "${GREEN}${BOLD}All tests passed! 🎉${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Verify functionality manually on each platform"
    echo "  2. Test with real users (Phase 2 testers)"
    echo "  3. Proceed to Phase 3 (public release) when ready"
    echo ""
    echo -e "${BLUE}Ready to proceed to Phase 3!${NC}"
    exit 0
fi
