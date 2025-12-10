#!/bin/bash
set -e

echo "=== Docker/OCI Installation Validation ==="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found"
    exit 1
fi
echo "✓ Docker found"

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon not running"
    echo "Start with: sudo systemctl start docker"
    exit 1
fi
echo "✓ Docker daemon running"

# Set image name
IMAGE="${IMAGE:-ghcr.io/hollowsunhc/provenance-demo:latest}"

# Check if image exists locally
if ! docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "$IMAGE"; then
    echo "⚠️  Image not found locally, pulling..."
    docker pull "$IMAGE"
fi
echo "✓ Image available: $IMAGE"

# Check version
VERSION=$(docker run --rm "$IMAGE" --version 2>&1)
if [[ -z "$VERSION" ]]; then
    echo "❌ Version check failed"
    exit 1
fi
echo "✓ Version: $VERSION"

# Test basic functionality
OUTPUT=$(docker run --rm "$IMAGE" hello "Test" 2>&1)
if [[ "$OUTPUT" != *"Hello, Test"* ]]; then
    echo "❌ Basic functionality test failed"
    exit 1
fi
echo "✓ Basic functionality works"

# Verify image metadata
CREATED=$(docker inspect "$IMAGE" --format='{{.Created}}')
SIZE=$(docker inspect "$IMAGE" --format='{{.Size}}' | numfmt --to=iec 2>/dev/null || docker inspect "$IMAGE" --format='{{.Size}}')
echo "✓ Image created: $CREATED"
echo "✓ Image size: $SIZE"

# Check if cosign is available for verification
if command -v cosign &> /dev/null; then
    echo "✓ cosign available for signature verification"
    # Note: Actual verification requires proper setup
else
    echo "⚠️  cosign not installed (optional)"
fi

echo ""
echo "✅ All validation checks passed!"
echo "Docker installation is working correctly."
