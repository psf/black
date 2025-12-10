#!/bin/bash
set -e

echo "=== Snap Installation Validation ==="

# Check if snapd is running
if ! systemctl is-active --quiet snapd; then
    echo "❌ snapd service not running"
    echo "Run: sudo systemctl start snapd"
    exit 1
fi
echo "✓ snapd service running"

# Check if snap is installed
if ! snap list | grep -q provenance-demo; then
    echo "❌ provenance-demo snap not installed"
    exit 1
fi
echo "✓ Snap installed"

# Check command exists
if ! command -v provenance-demo &> /dev/null; then
    echo "❌ provenance-demo command not found"
    echo "Try: sudo snap alias provenance-demo.provenance-demo provenance-demo"
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

# Check snap info
CHANNEL=$(snap info provenance-demo | grep "tracking:" | awk '{print $2}')
echo "✓ Channel: $CHANNEL"

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

# Check confinement
CONFINEMENT=$(snap info provenance-demo | grep "confinement:" | awk '{print $2}')
echo "✓ Confinement: $CONFINEMENT"

# Check snap health
if ! snap warnings | grep -q "No warnings"; then
    echo "⚠️  Snap warnings present"
    snap warnings
fi

echo ""
echo "✅ All validation checks passed!"
echo "Installation is working correctly."
