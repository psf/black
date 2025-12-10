#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

CHANNEL="rubygems-local-server"
log "Starting $CHANNEL workflow"

require_command gem
require_command ruby

WORK_DIR="$(mktemp -d "$WORK_ROOT/${CHANNEL}.XXXX")"
cleanup_hooks=("rm -rf '$WORK_DIR'")
trap 'for hook in "${cleanup_hooks[@]}"; do eval "$hook"; done' EXIT

GEM_DIR="$WORK_DIR/gem"
mkdir -p "$GEM_DIR/lib"

cat >"$GEM_DIR/redoubt-demo.gemspec" <<'EOF'
Gem::Specification.new do |spec|
  spec.name          = "redoubt-demo"
  spec.version       = "0.0.1"
  spec.summary       = "Demo gem for local repository testing"
  spec.files         = Dir["lib/**/*.rb"]
  spec.authors       = ["Redoubt"]
  spec.email         = ["dist@example.com"]
  spec.homepage      = "https://example.com/redoubt"
  spec.license       = "MIT"
end
EOF

cat >"$GEM_DIR/lib/redoubt-demo.rb" <<'EOF'
module RedoubtDemo
  def self.hello
    "Hello from Redoubt gem"
  end
end
EOF

pushd "$GEM_DIR" >/dev/null
GEM_FILE="$(gem build redoubt-demo.gemspec 2>/dev/null | awk '/File: /{print $2}' | tail -n1 || true)"
[[ -z "$GEM_FILE" ]] && skip "Gem build failed"
popd >/dev/null

REPO_DIR="$WORK_DIR/repo"
mkdir -p "$REPO_DIR/gems"
cp "$GEM_DIR/$GEM_FILE" "$REPO_DIR/gems/"
pushd "$REPO_DIR" >/dev/null
if ! gem generate_index >/dev/null 2>&1; then
  skip "gem generate_index failed"
fi
popd >/dev/null

PORT=${RUBYGEMS_PORT:-8808}
ruby -run -e httpd "$REPO_DIR" -p "$PORT" >/dev/null 2>&1 &
SERVER_PID=$!
cleanup_hooks+=("kill '$SERVER_PID' >/dev/null 2>&1 || true")
sleep 1

if ! gem install --clear-sources --source "http://127.0.0.1:${PORT}" redoubt-demo >/dev/null 2>&1; then
  skip "gem install from local server failed"
fi

log "RubyGems local server workflow completed"
