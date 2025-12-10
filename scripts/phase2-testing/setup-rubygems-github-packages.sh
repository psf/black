#!/usr/bin/env bash
set -euo pipefail
: "${GITHUB_TOKEN:?Set GITHUB_TOKEN}"
: "${GITHUB_ACTOR:?Set GITHUB_ACTOR username}"

mkdir -p ~/.gem
cat > ~/.gem/credentials <<EOF
---
:github: Bearer ${GITHUB_TOKEN}
EOF
chmod 0600 ~/.gem/credentials
echo "✓ RubyGems configured for GitHub Packages"
