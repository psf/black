#!/bin/bash
# Usage:
# docker build -t black_gallery .
# docker run -it \
#    -v /host/directory/for/output:/output black_gallery:latest \
#    -p Twisted \
#    19.10b0:pyproject-19.10b0.toml \
#    master:pyproject-master.toml

set -e

git config --global user.email "nobody@example.com"
git config --global user.name "BlackBot"

BLACK_VERSIONS=()
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
  -p)
    PROJECT="$2"
    shift # past argument
    shift # past value
    ;;
  -v)
    PROJECT_VERSION="$2"
    shift # past argument
    shift # past value
    ;;
  *)
    BLACK_VERSIONS+=("$1")
    shift
    ;;

  esac
done
set -- "${BLACK_VERSIONS[@]}"

if [ -z "${PROJECT}" ]; then
  echo "Provide a package with -p"
  exit 1
fi

if [ ! -z "${PROJECT_VERSION}" ]; then
  PROJECT="${PROJECT}==${PROJECT_VERSION}"
fi

# Bail on undefined variables
set -u

if [ ${#BLACK_VERSIONS[@]} -eq 0 ]; then
  BLACK_VERSIONS+=("master")
fi

echo "Package: ${PROJECT}"
echo "Black versions: ${BLACK_VERSIONS[*]}"

echo "------------------------------------"
read -p "Continue? " -n 1 -r
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo " Aborting."
  exit 1
fi

for bv in "${BLACK_VERSIONS[@]}"; do
  BLACK_PKG="Black==${bv}"
  TARGET="/output/${bv}/${PROJECT}"
  BRANCH="black-${bv}"
  mkdir -p "${TARGET}"
  echo "Installing ${BLACK_PKG}"
  echo "Running pip install --prefix=${TARGET} ${PROJECT}"
  pip install "--prefix=${TARGET}" "${PROJECT}"

  cd "${TARGET}"
  git init .
  git add .
  git commit -m "Initial commit"

  # create a new branch (reset if it already exists)
  git checkout -B "${BRANCH}"

  echo "Formatting ${PROJECT} with ${BLACK_PKG}; outputting to ${TARGET}"
  black "${TARGET}"
  git add .
  git commit -m "Formatted with Black version ${bv}"
  git checkout master
  echo "--- finished | Black version ${bv} | Package ${PROJECT} | branch ${BRANCH} | target dir ${TARGET}"
done
exit 0


# -p Django -v 3.0.3 master
