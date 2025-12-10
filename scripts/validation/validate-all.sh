#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Help message
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Master validation script that runs all platform validation scripts.

OPTIONS:
    --help              Show this help message
    --platforms=LIST    Comma-separated list of platforms to validate
                        Available: pypi,pipx,pyz,github-releases,homebrew,snap,docker
                        Default: all platforms
    --continue-on-error Continue validation even if a platform fails
    --verbose           Show detailed output from each validation script

EXAMPLES:
    # Validate all platforms
    $(basename "$0")

    # Validate specific platforms
    $(basename "$0") --platforms=pypi,docker

    # Continue validation even if some fail
    $(basename "$0") --continue-on-error

    # Verbose mode
    $(basename "$0") --verbose

PLATFORMS:
    pypi              - PyPI (pip/uv) installation
    pipx              - pipx installation
    pyz               - Direct .pyz execution
    github-releases   - GitHub Releases download
    homebrew          - Homebrew installation
    snap              - Snap package
    docker            - Docker/OCI container

EXIT CODES:
    0 - All validations passed
    1 - One or more validations failed
EOF
}

# Default settings
CONTINUE_ON_ERROR=false
VERBOSE=false
PLATFORMS=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            show_help
            exit 0
            ;;
        --platforms=*)
            PLATFORMS="${1#*=}"
            shift
            ;;
        --continue-on-error)
            CONTINUE_ON_ERROR=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define all available platforms
ALL_PLATFORMS=(
    "pypi"
    "pipx"
    "pyz"
    "github-releases"
    "homebrew"
    "snap"
    "docker"
)

# Parse platform list
if [[ -n "$PLATFORMS" ]]; then
    IFS=',' read -ra PLATFORM_ARRAY <<< "$PLATFORMS"
else
    PLATFORM_ARRAY=("${ALL_PLATFORMS[@]}")
fi

# Validation results
declare -A RESULTS
TOTAL=0
PASSED=0
FAILED=0
SKIPPED=0

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Platform Validation - Master Script                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Run validations
for platform in "${PLATFORM_ARRAY[@]}"; do
    SCRIPT="${SCRIPT_DIR}/validate-${platform}.sh"
    TOTAL=$((TOTAL + 1))

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Testing: ${platform}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Check if script exists
    if [[ ! -f "$SCRIPT" ]]; then
        echo -e "${YELLOW}⚠️  Validation script not found: $SCRIPT${NC}"
        RESULTS[$platform]="SKIPPED"
        SKIPPED=$((SKIPPED + 1))
        echo ""
        continue
    fi

    # Make script executable if needed
    if [[ ! -x "$SCRIPT" ]]; then
        chmod +x "$SCRIPT"
    fi

    # Run validation
    if [[ "$VERBOSE" == true ]]; then
        if bash "$SCRIPT"; then
            RESULTS[$platform]="PASSED"
            PASSED=$((PASSED + 1))
        else
            RESULTS[$platform]="FAILED"
            FAILED=$((FAILED + 1))
            if [[ "$CONTINUE_ON_ERROR" == false ]]; then
                echo -e "${RED}Validation failed. Use --continue-on-error to continue anyway.${NC}"
                break
            fi
        fi
    else
        OUTPUT=$(bash "$SCRIPT" 2>&1)
        EXIT_CODE=$?

        if [[ $EXIT_CODE -eq 0 ]]; then
            echo -e "${GREEN}✓ Validation passed${NC}"
            RESULTS[$platform]="PASSED"
            PASSED=$((PASSED + 1))
        else
            echo -e "${RED}✗ Validation failed${NC}"
            echo ""
            echo "Output:"
            echo "$OUTPUT"
            RESULTS[$platform]="FAILED"
            FAILED=$((FAILED + 1))

            if [[ "$CONTINUE_ON_ERROR" == false ]]; then
                echo ""
                echo -e "${RED}Validation failed. Use --continue-on-error to continue anyway.${NC}"
                break
            fi
        fi
    fi

    echo ""
done

# Summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    VALIDATION SUMMARY                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Show results table
printf "%-20s %s\n" "Platform" "Result"
echo "────────────────────────────────────────────────────────────────"

for platform in "${PLATFORM_ARRAY[@]}"; do
    result="${RESULTS[$platform]}"

    case $result in
        PASSED)
            printf "%-20s ${GREEN}✓ PASSED${NC}\n" "$platform"
            ;;
        FAILED)
            printf "%-20s ${RED}✗ FAILED${NC}\n" "$platform"
            ;;
        SKIPPED)
            printf "%-20s ${YELLOW}⊘ SKIPPED${NC}\n" "$platform"
            ;;
        *)
            printf "%-20s ${YELLOW}? UNKNOWN${NC}\n" "$platform"
            ;;
    esac
done

echo ""
echo "────────────────────────────────────────────────────────────────"
echo "Total:   $TOTAL"
echo -e "Passed:  ${GREEN}$PASSED${NC}"
echo -e "Failed:  ${RED}$FAILED${NC}"
echo -e "Skipped: ${YELLOW}$SKIPPED${NC}"
echo "────────────────────────────────────────────────────────────────"
echo ""

# Exit with appropriate code
if [[ $FAILED -gt 0 ]]; then
    echo -e "${RED}❌ Some validations failed${NC}"
    exit 1
else
    echo -e "${GREEN}✅ All validations passed!${NC}"
    exit 0
fi
