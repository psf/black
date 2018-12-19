#!/bin/bash

BASEDIR=$(dirname "$0")
VERSION="latest"
IMAGENAME="ambv/black"

if [ -n "$(docker images -q "${IMAGENAME}:${VERSION}" 2> /dev/null)" ]; then
  TAG="$(grep -iR "^__version__ =" "${BASEDIR}"/../black.py | awk -F "= " '{print $2}' | sed 's/"//g')"
  docker tag "${IMAGENAME}:${VERSION}" "${IMAGENAME}:${TAG}"
  echo "tagged image ${IMAGENAME}:${TAG}"
fi
