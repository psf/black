#!/bin/bash
set -e

echo "=== GitHub Release Download Validation ==="

# Configuration
VERSION="${VERSION:-v0.0.1-alpha.40}"
REPO="${REPO:-hollowsunhc/provenance-template}"
FILE="${FILE:-provenance-demo.pyz}"

# Check if file exists
if [[ ! -f "$FILE" ]]; then
    echo "❌ $FILE not found"
    exit 1
fi
echo "✓ File downloaded: $FILE"

# Check if checksums file exists
if [[ ! -f "checksums.txt" ]]; then
    echo "⚠️  checksums.txt not found (recommended for verification)"
else
    # Verify checksum
    EXPECTED=$(grep "$FILE" checksums.txt | awk '{print $1}')
    ACTUAL=$(sha256sum "$FILE" | awk '{print $1}')
    if [[ "$EXPECTED" != "$ACTUAL" ]]; then
        echo "❌ Checksum mismatch!"
        echo "Expected: $EXPECTED"
        echo "Actual: $ACTUAL"
        exit 1
    fi
    echo "✓ Checksum verified"
fi

# Make executable (for .pyz)
if [[ "$FILE" == *.pyz ]]; then
    chmod +x "$FILE"
    echo "✓ Made executable"
fi

# Check version
if [[ "$FILE" == *.pyz ]]; then
    VERSION_OUTPUT=$(./"$FILE" --version 2>&1)
elif [[ "$FILE" == *.whl ]] || [[ "$FILE" == *.tar.gz ]]; then
    pip install "$FILE" -q
    VERSION_OUTPUT=$(provenance-demo --version 2>&1)
fi

if [[ -z "$VERSION_OUTPUT" ]]; then
    echo "❌ Version check failed"
    exit 1
fi
echo "✓ Version: $VERSION_OUTPUT"

# Test basic functionality
if [[ "$FILE" == *.pyz ]]; then
    OUTPUT=$(./"$FILE" hello "Test" 2>&1)
else
    OUTPUT=$(provenance-demo hello "Test" 2>&1)
fi

if [[ "$OUTPUT" != *"Hello, Test"* ]]; then
    echo "❌ Basic functionality test failed"
    exit 1
fi
echo "✓ Basic functionality works"

# Check Sigstore signature if available
if command -v cosign &> /dev/null; then
    if [[ -f "$FILE.sig" ]] && [[ -f "$FILE.crt" ]]; then
        if cosign verify-blob "$FILE" \
            --signature "$FILE.sig" \
            --certificate "$FILE.crt" \
            --certificate-identity-regexp="https://github.com/$REPO" \
            --certificate-oidc-issuer="https://token.actions.githubusercontent.com" &> /dev/null; then
            echo "✓ Sigstore signature verified"
        else
            echo "⚠️  Sigstore verification failed"
        fi
    else
        echo "⚠️  Signature files not found (optional)"
    fi
else
    echo "⚠️  cosign not installed (optional)"
fi

echo ""
echo "✅ All validation checks passed!"
echo "Download is working correctly."
