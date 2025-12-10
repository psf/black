#!/usr/bin/env bash
set -euo pipefail
REPO_DIR="${1:-dist/deb-repo}"

if [[ ! -d "$REPO_DIR" ]]; then
  echo "repo dir not found: $REPO_DIR"; exit 1
fi

pushd "$REPO_DIR" >/dev/null
if [[ ! -f "dists/stable/main/binary-amd64/Packages" ]]; then
  echo "Expected Packages file under dists/... not found. Ensure your repo layout is correct."; exit 2
fi

cat > Release <<'EOF'
Origin: Redoubt
Label: Redoubt
Suite: stable
Codename: stable
Architectures: amd64 arm64
Components: main
Description: Redoubt APT repository
EOF

# embed hashes for Packages
for f in $(find dists -type f -name 'Packages' -o -name 'Packages.gz' -o -name 'Packages.xz'); do
  sz=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f")
  sha256=$(sha256sum "$f" 2>/dev/null | awk '{print $1}' || shasum -a 256 "$f" | awk '{print $1}')
  echo "SHA256:" >> Release
  echo " $sha256 $sz $f" >> Release
done
popd >/dev/null

echo "✓ APT Release file generated at $REPO_DIR/Release (ready for signing)"
