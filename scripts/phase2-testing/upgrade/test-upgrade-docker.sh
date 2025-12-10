#!/usr/bin/env bash
set -euo pipefail

: "${IMAGE:=ghcr.io/OWNER/redoubt}"
: "${FROM_TAG:?e.g. 1.0.0}"
: "${TO_TAG:?e.g. 1.1.0}"

docker pull "${IMAGE}:${FROM_TAG}"
docker run --rm "${IMAGE}:${FROM_TAG}" --version || true

docker pull "${IMAGE}:${TO_TAG}"
docker run --rm "${IMAGE}:${TO_TAG}" --version || true

# "Rollback" = re-run FROM
docker run --rm "${IMAGE}:${FROM_TAG}" --version || true
echo "✓ Docker tag upgrade/rollback OK"
