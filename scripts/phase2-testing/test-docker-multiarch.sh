#!/usr/bin/env bash
set -euo pipefail

IMG="${1:-ghcr.io/OWNER/redoubt:test}"

if [[ "$IMG" =~ ^ghcr\.io ]]; then
  if ! docker info 2>/dev/null | grep -q "Username:"; then
    echo "Not logged into GHCR."
    echo 'Run: echo "$GITHUB_TOKEN" | docker login ghcr.io -u USERNAME --password-stdin'
    exit 1
  fi
fi

docker buildx inspect multiarch-builder >/dev/null 2>&1 || docker buildx create --use --name multiarch-builder
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
docker buildx build --platform linux/amd64,linux/arm64 -t "$IMG" --push .
echo "✓ Pushed multi-arch image: $IMG"