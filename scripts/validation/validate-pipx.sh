#!/bin/bash
set -e

echo "=== pipx Installation Validation ==="

# Check if pipx is installed
if ! command -v pipx &> /dev/null; then
    echo "❌ pipx not found"
    exit 1
fi
echo "✓ pipx found"

# Check command exists
if ! command -v provenance-demo &> /dev/null; then
    echo "❌ provenance-demo command not found"
    exit 1
fi
echo "✓ Command found"

# Check version
VERSION=$(provenance-demo --version 2>&1)
if [[ -z "$VERSION" ]]; then
    echo "❌ Version check failed"
    exit 1
fi
echo "✓ Version: $VERSION"

# Verify pipx shows the package
if ! pipx list | grep -q "provenance-demo"; then
    echo "❌ Package not in pipx list"
    exit 1
fi
echo "✓ Package registered with pipx"

# Test basic functionality
OUTPUT=$(provenance-demo hello "Test" 2>&1)
if [[ "$OUTPUT" != *"Hello, Test"* ]]; then
    echo "❌ Basic functionality test failed"
    exit 1
fi
echo "✓ Basic functionality works"

# Check if verify command exists
if ! provenance-demo verify --help &> /dev/null; then
    echo "❌ Verify command not available"
    exit 1
fi
echo "✓ Verify command available"

echo ""
echo "✅ All validation checks passed!"
echo "Installation is working correctly."
