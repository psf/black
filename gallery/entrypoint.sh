#!/bin/bash

set -e


BLACK_VERSIONS=()
while [[ $# -gt 0 ]]; do
    key="$1"
    echo "processing key $key"

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
    echo "Error: Must specify a package with -p"
    exit 1
fi

# Bail on undefined variables from here on out
# set -u

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

get_source_for_project() {
    project="$1"
    version="$2"
    target="/output/${project}"
    mkdir -p "${target}"

    case "${project}" in
    cpython)
        src="https://github.com/python/cpython/archive/${version}.zip"
        echo "getting source: ${src}"
        wget "${src}" -P /tmp
        unzip -qd "${target}" master.zip
        ;;
    mypy)
        src="https://foss.heptapod.net/pypy/pypy/repository/${version}/archive.tar.bz2"
        echo "getting source: ${src}"
        wget -O- "${src}" | tar -xjf - -C "${target}"
        ;;
    *)
        if [ ! -z "${version}" ]; then
            project="${project}==${version}"
        fi
        echo "Running: pip install --quiet --no-warn-script-location --no-deps --no-binary all --no-cache '--prefix=${target}' '${project}'"
        pip install --quiet --no-warn-script-location --no-deps --no-binary all --no-cache "--prefix=${target}" "${project}"
        ;;
    esac

    echo "${target}"
}

get_black() {
    version="$1"
    BLACK_PKG="Black==${version}"
    echo "Installing ${BLACK_PKG}"
    if [[ $version == "master" ]]; then
        pip install --quiet --force-reinstall git+https://github.com/psf/black.git
    else
        pip install --quiet --force-reinstall "${BLACK_PKG}"
    fi
}

TARGET=$(get_source_for_project "${PROJECT}" "${PROJECT_VERSION}")

TARGET="/output/"
cd "${TARGET}"
git init .
git config --local user.email "nobody@example.com"
git config --local user.name "BlackBot"
git add .
git commit -q -m "Initial commit"

for bv in "${BLACK_VERSIONS[@]}"; do

    # extract .toml file if present
    IFS=':'
    read -ra PAIR <<<"${bv}" # split version string using ':' as delimiter
    if [ ${#PAIR[@]} -gt 1 ]; then
        bv=${PAIR[0]}
        toml=${PAIR[1]}
        echo "found toml: ${toml}"
        echo "black version: ${bv}"
    fi
    IFS=' '

    CONFIG=""
    if [ ! -z "${toml}" ] && [ ! -f "${toml}" ]; then
        echo "You specified file ${toml} but it doesn't exist, did you mount it?"
        echo "directory listing:"
        ls -la
        exit 1
    else
        CONFIG="--config ${toml}"
    fi


    BLACK_PKG=$(get_black "${bv}")
    BRANCH="black-${bv}"

    # create a new branch (or reset if it already exists)
    git checkout -B "${BRANCH}"

    echo "Formatting ${PROJECT} with ${BLACK_PKG}; outputting to ${TARGET}"
    black --version
    # shellcheck disable=SC2086
    black ${CONFIG} "${TARGET}"
    git add .
    git commit -m "Formatted with Black version ${bv}"
    git checkout master
    echo "--- finished | Black version ${bv} | Package ${PROJECT} | branch ${BRANCH} | target dir ${TARGET}"
done
