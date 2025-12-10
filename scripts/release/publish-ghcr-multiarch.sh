#!/usr/bin/env bash
set -euo pipefail
: "${IMAGE:?e.g. ghcr.io/OWNER/redoubt}"
: "${TAG:?e.g. 1.1.0}"

docker buildx inspect multiarch >/dev/null 2>&1 || docker buildx create --use --name multiarch
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
docker buildx build --platform linux/amd64,linux/arm64 -t "${IMAGE}:${TAG}" --push .
echo "✓ pushed ${IMAGE}:${TAG} (multi-arch)"
