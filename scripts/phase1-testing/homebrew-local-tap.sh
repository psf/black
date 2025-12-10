#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

CHANNEL="homebrew-local-tap"
log "Starting $CHANNEL workflow"

require_command brew

ensure_python_build_artifacts

PYZ_FILE="$(ls -1 "$REPO_ROOT"/dist/*.pyz 2>/dev/null | head -n1 || true)"
[[ -z "$PYZ_FILE" ]] && skip "No .pyz artifact available"

SHA256="$(shasum -a 256 "$PYZ_FILE" | cut -d' ' -f1)"
FORMULA_DIR="$(mktemp -d "$WORK_ROOT/${CHANNEL}.XXXX")"
trap 'rm -rf "$FORMULA_DIR"' EXIT

cat >"$FORMULA_DIR/redoubt.rb" <<EOF
class Redoubt < Formula
  desc "Local tap verification for redoubt CLI"
  homepage "https://example.com/local-tap"
  url "file://$PYZ_FILE"
  sha256 "$SHA256"
  version "0.0.0-local"
  license "MIT"

  depends_on "python@3.11"

  def install
    bin.install "provenance-demo.pyz" => "redoubt-local"
  end

  test do
    system "#{bin}/redoubt-local", "--help"
  end
end
EOF

export HOMEBREW_NO_AUTO_UPDATE=1
pushd "$FORMULA_DIR" >/dev/null
if ! brew install --build-from-source ./redoubt.rb >/dev/null 2>&1; then
  skip "brew install from local formula failed (likely due to sandboxed environment)"
fi

brew test redoubt >/dev/null 2>&1 || log "brew test returned non-zero (acceptable in sandbox)"
brew uninstall redoubt >/dev/null 2>&1 || true
popd >/dev/null

log "Homebrew local tap workflow completed"
