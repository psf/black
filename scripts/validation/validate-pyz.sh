#!/bin/bash
set -e

echo "=== .pyz Installation Validation ==="

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ "$PYTHON_VERSION" < "3.10" ]]; then
    echo "❌ Python 3.10+ required (found: $PYTHON_VERSION)"
    exit 1
fi
echo "✓ Python version: $PYTHON_VERSION"

# Check if .pyz file exists
if [[ ! -f "provenance-demo.pyz" ]]; then
    echo "❌ provenance-demo.pyz not found in current directory"
    exit 1
fi
echo "✓ .pyz file found"

# Check if executable
if [[ ! -x "provenance-demo.pyz" ]]; then
    echo "❌ File is not executable"
    echo "Run: chmod +x provenance-demo.pyz"
    exit 1
fi
echo "✓ File is executable"

# Check version
VERSION=$(./provenance-demo.pyz --version 2>&1)
if [[ -z "$VERSION" ]]; then
    echo "❌ Version check failed"
    exit 1
fi
echo "✓ Version: $VERSION"

# Test basic functionality
OUTPUT=$(./provenance-demo.pyz hello "Test" 2>&1)
if [[ "$OUTPUT" != *"Hello, Test"* ]]; then
    echo "❌ Basic functionality test failed"
    exit 1
fi
echo "✓ Basic functionality works"

# Check if verify command exists
if ! ./provenance-demo.pyz verify --help &> /dev/null; then
    echo "❌ Verify command not available"
    exit 1
fi
echo "✓ Verify command available"

# Verify file integrity (if checksums.txt exists)
if [[ -f "checksums.txt" ]]; then
    EXPECTED=$(grep "provenance-demo.pyz" checksums.txt | awk '{print $1}')
    ACTUAL=$(sha256sum provenance-demo.pyz | awk '{print $1}')
    if [[ "$EXPECTED" != "$ACTUAL" ]]; then
        echo "❌ Checksum mismatch!"
        echo "Expected: $EXPECTED"
        echo "Actual: $ACTUAL"
        exit 1
    fi
    echo "✓ Checksum verified"
fi

echo ""
echo "✅ All validation checks passed!"
echo "Installation is working correctly."
