#!/bin/bash
# Black format comparison helper
# For details, see https://github.com/psf/black/issues/1290

set -e # bail on error

prepare() {
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
    echo # newline, for aesthetics
}

get_source_for_project() {
    project="$1"
    version="$2"
    target="${TARGET}${project}"

    [ -e "${target}" ] && echo "[WARNING] Path already exists: ${target}"
    mkdir -p "${target}"

    case "${project}" in
    cpython)
        version="${version:-master}" # assume "master" if version not specified
        src="https://github.com/python/cpython/archive/${version}.zip"
        echo "getting source: ${src}"
        wget "${src}" -P /tmp
        unzip -qd "${target}" "/tmp/${version}.zip"
        ;;
    mypy)
        version="${version:-branch/default}" # assume "branch/default" if version not specified
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
    version=${1:-master} # Assume "master" if version not provided

    if [[ $version == "master" ]]; then
        src="git+https://github.com/psf/black.git"
    else
        src="Black==${version}"
    fi

    echo "Installing ${src}"
    pip install --quiet --force-reinstall "${src}"
}

get_config_str() {
    toml="$1"
    if [ ! -z "${toml}" ]; then
        if [ ! -f "${toml}" ]; then
            echo >&2 "[ERROR] You specified file ${toml} but it doesn't exist, did you mount it?"
            echo >&2 "directory listing:"
            ls >&2 -la
            exit 1
        else
            echo "--config ${toml}"
        fi
    fi
}

init_git() {
    cd "${1}"
    echo "Initializing git repository in ${1}."
    if [ -d ".git" ]; then
        echo "[WARNING] .git directory already exists."
    fi

    git init .
    git add .
    git commit -q -m "Initial commit"
}

main() {
    for bv in "${BLACK_VERSIONS[@]}"; do

        # extract .toml file if present
        IFS=':'
        read -ra PAIR <<<"${bv}" # split version string using ':' as delimiter
        if [ ${#PAIR[@]} -gt 1 ]; then
            bv=${PAIR[0]}
            toml=${PAIR[1]}
            echo "black version: ${bv}"
            echo "requested toml: ${toml}"
        fi
        IFS=' '

        config=$(get_config_str "${toml}")
        init_git "${TARGET}"
        get_black "${bv}"
        black --version

        # create a new branch (-B will reset if it already exists)
        branch="black-${bv}"
        git checkout -B "${branch}"

        echo "Formatting ${PROJECT} with ${bv}; outputting to ${TARGET}"
        # shellcheck disable=SC2086
        black ${config} "${TARGET}"

        git add .
        git commit -m "Formatted with Black version ${bv}"
        git checkout master
        echo "--- finished | Black version ${bv} | Package ${PROJECT} | branch ${branch} | target dir ${TARGET}"
    done
}

TARGET="/output/"
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
    echo "Error: Must specify a package with -p"
    exit 1
fi

prepare
get_source_for_project "${PROJECT}" "${PROJECT_VERSION}"
main
