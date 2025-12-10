#!/bin/bash
set -e

echo "=== Homebrew Installation Validation ==="

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found"
    exit 1
fi
echo "✓ Homebrew found"

# Check if package is installed
if ! brew list provenance-demo &> /dev/null; then
    echo "❌ provenance-demo not installed via Homebrew"
    exit 1
fi
echo "✓ Package installed via Homebrew"

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

# Verify installation path
INSTALL_PATH=$(brew --prefix provenance-demo)
if [[ ! -d "$INSTALL_PATH" ]]; then
    echo "❌ Installation directory not found"
    exit 1
fi
echo "✓ Installed at: $INSTALL_PATH"

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

# Verify no issues
ISSUES=$(brew doctor 2>&1 | grep -i provenance-demo || true)
if [[ -n "$ISSUES" ]]; then
    echo "⚠️  Homebrew doctor found issues:"
    echo "$ISSUES"
fi

echo ""
echo "✅ All validation checks passed!"
echo "Installation is working correctly."
