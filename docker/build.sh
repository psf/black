#!/bin/bash

BASEDIR=$(dirname "$0")
VERSION="latest"
IMAGENAME="ambv/black"

docker build -t ${IMAGENAME}:"${VERSION}" -f "${BASEDIR}"/Dockerfile "${BASEDIR}"
