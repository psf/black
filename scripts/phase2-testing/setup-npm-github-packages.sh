#!/usr/bin/env bash
set -euo pipefail
: "${GITHUB_TOKEN:?Set GITHUB_TOKEN for GitHub Packages}"
: "${GITHUB_ACTOR:?Set GITHUB_ACTOR username}"
: "${NPM_SCOPE:?Set NPM_SCOPE, e.g. @OWNER}"

npm set //npm.pkg.github.com/:_authToken="$GITHUB_TOKEN"
npm set "@${NPM_SCOPE#:}:registry" "https://npm.pkg.github.com/"

echo "✓ npm configured for GitHub Packages"
