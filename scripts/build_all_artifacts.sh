#!/usr/bin/env bash
# Build every distribution artifact used by the release pipeline.
# Generates Python artifacts (wheel, sdist, zipapp) and packages
# distribution manifests for downstream platforms in tarballs.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST_DIR="$REPO_ROOT/dist"

echo "🚀 Building full distribution artifact set"

mkdir -p "$DIST_DIR"

echo "→ Ensuring build tooling is installed"
if ! python -c "import build" >/dev/null 2>&1; then
  python -m pip install --upgrade pip==24.3.1 >/dev/null 2>&1
  python -m pip install --upgrade build==1.2.2.post1 >/dev/null 2>&1
fi

echo "→ Building Python wheel and source archive"
rm -rf "$DIST_DIR"/*
python -m build --outdir "$DIST_DIR"

echo "→ Building executable zipapp"
rm -rf "$REPO_ROOT/build/pyz"
mkdir -p "$REPO_ROOT/build/pyz/src"
rsync -a "$REPO_ROOT/src/" "$REPO_ROOT/build/pyz/src/"
python -m zipapp "$REPO_ROOT/build/pyz/src" \
  -m "demo_cli.cli:main" \
  -o "$DIST_DIR/provenance-demo.pyz"
chmod +x "$DIST_DIR/provenance-demo.pyz"

echo "→ Capturing distribution manifests"

declare -a distribution_dirs=(
  "packaging/appimage"
  "packaging/aur"
  "packaging/chocolatey"
  "packaging/debian"
  "packaging/flatpak"
  "packaging/homebrew-tap"
  "packaging/rpm"
  "packaging/scoop"
  "packaging/snap"
  "packaging/winget"
  "scripts/phase1-testing"
  "scripts/phase2-testing"
  "docs/distribution"
)

archives=()

for directory in "${distribution_dirs[@]}"; do
  name="$(basename "$directory")"
  archive="$DIST_DIR/distribution-${name}.tar.gz"
  echo "   • Archiving $directory -> $archive"
  tar -czf "$archive" -C "$REPO_ROOT" "$directory"
  archives+=("$(basename "$archive")")
done

echo "→ Writing artifact manifest"
generated_at="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
cat > "$DIST_DIR/distribution-manifest.json" <<JSON
{
  "artifacts": [
    "python-wheel",
    "python-sdist",
    "python-zipapp",
    "packaging-manifests",
    "distribution-test-harnesses",
    "distribution-documentation"
  ],
  "generated_at": "$generated_at",
  "archives": [
$(for archive in "${archives[@]}"; do printf '    "%s",\n' "$archive"; done | sed '$s/,$//')
  ]
}
JSON

echo "✅ Full distribution bundle available in dist/"
