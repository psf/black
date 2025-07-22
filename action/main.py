import os
import re
import shlex
import shutil
import sys
from pathlib import Path
from subprocess import PIPE, STDOUT, run
from typing import Union

ACTION_PATH = Path(os.environ["GITHUB_ACTION_PATH"])
ENV_PATH = ACTION_PATH / ".black-env"
ENV_BIN = ENV_PATH / ("Scripts" if sys.platform == "win32" else "bin")
OPTIONS = os.getenv("INPUT_OPTIONS", default="")
SRC = os.getenv("INPUT_SRC", default="")
JUPYTER = os.getenv("INPUT_JUPYTER") == "true"
BLACK_ARGS = os.getenv("INPUT_BLACK_ARGS", default="")
VERSION = os.getenv("INPUT_VERSION", default="")
USE_PYPROJECT = os.getenv("INPUT_USE_PYPROJECT") == "true"

BLACK_VERSION_RE = re.compile(r"^black([^A-Z0-9._-]+.*)$", re.IGNORECASE)
EXTRAS_RE = re.compile(r"\[.*\]")
EXPORT_SUBST_FAIL_RE = re.compile(r"\$Format:.*\$")


def determine_version_specifier() -> str:
    """Determine the version of Black to install.

    The version can be specified either via the `with.version` input or via the
    pyproject.toml file if `with.use_pyproject` is set to `true`.
    """
    if USE_PYPROJECT and VERSION:
        print(
            "::error::'with.version' and 'with.use_pyproject' inputs are "
            "mutually exclusive.",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)
    if USE_PYPROJECT:
        return read_version_specifier_from_pyproject()
    elif VERSION and VERSION[0] in "0123456789":
        return f"=={VERSION}"
    else:
        return VERSION


def read_version_specifier_from_pyproject() -> str:
    if sys.version_info < (3, 11):
        print(
            "::error::'with.use_pyproject' input requires Python 3.11 or later.",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)

    import tomllib  # type: ignore[import-not-found,unreachable]

    try:
        with Path("pyproject.toml").open("rb") as fp:
            pyproject = tomllib.load(fp)
    except FileNotFoundError:
        print(
            "::error::'with.use_pyproject' input requires a pyproject.toml file.",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)

    version = pyproject.get("tool", {}).get("black", {}).get("required-version")
    if version is not None:
        return f"=={version}"

    arrays = [
        *pyproject.get("dependency-groups", {}).values(),
        pyproject.get("project", {}).get("dependencies"),
        *pyproject.get("project", {}).get("optional-dependencies", {}).values(),
    ]
    for array in arrays:
        version = find_black_version_in_array(array)
        if version is not None:
            break

    if version is None:
        print(
            "::error::'black' dependency missing from pyproject.toml.",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)

    return version


def find_black_version_in_array(array: object) -> Union[str, None]:
    if not isinstance(array, list):
        return None
    try:
        for item in array:
            # Rudimentary PEP 508 parsing.
            item = item.split(";")[0]
            item = EXTRAS_RE.sub("", item).strip()
            if item == "black":
                print(
                    "::error::Version specifier missing for 'black' dependency in "
                    "pyproject.toml.",
                    file=sys.stderr,
                    flush=True,
                )
                sys.exit(1)
            elif m := BLACK_VERSION_RE.match(item):
                return m.group(1).strip()
    except TypeError:
        pass

    return None


run([sys.executable, "-m", "venv", str(ENV_PATH)], check=True)

version_specifier = determine_version_specifier()
if JUPYTER:
    extra_deps = "[colorama,jupyter]"
else:
    extra_deps = "[colorama]"
if version_specifier:
    req = f"black{extra_deps}{version_specifier}"
else:
    describe_name = ""
    with open(ACTION_PATH / ".git_archival.txt", encoding="utf-8") as fp:
        for line in fp:
            if line.startswith("describe-name: "):
                describe_name = line[len("describe-name: ") :].rstrip()
                break
    if not describe_name:
        print("::error::Failed to detect action version.", file=sys.stderr, flush=True)
        sys.exit(1)
    # expected format is one of:
    # - 23.1.0
    # - 23.1.0-51-g448bba7
    # - $Format:%(describe:tags=true,match=*[0-9]*)$ (if export-subst fails)
    if (
        describe_name.count("-") < 2
        and EXPORT_SUBST_FAIL_RE.match(describe_name) is None
    ):
        # the action's commit matches a tag exactly, install exact version from PyPI
        req = f"black{extra_deps}=={describe_name}"
    else:
        # the action's commit does not match any tag, install from the local git repo
        req = f".{extra_deps}"
print(f"Installing {req}...", flush=True)
pip_proc = run(
    [str(ENV_BIN / "python"), "-m", "pip", "install", req],
    stdout=PIPE,
    stderr=STDOUT,
    encoding="utf-8",
    cwd=ACTION_PATH,
)
if pip_proc.returncode:
    print(pip_proc.stdout)
    print("::error::Failed to install Black.", file=sys.stderr, flush=True)
    sys.exit(pip_proc.returncode)


base_cmd = [str(ENV_BIN / "black")]
if BLACK_ARGS:
    # TODO: remove after a while since this is deprecated in favour of SRC + OPTIONS.
    proc = run(
        [*base_cmd, *shlex.split(BLACK_ARGS)],
        stdout=PIPE,
        stderr=STDOUT,
        encoding="utf-8",
    )
else:
    proc = run(
        [*base_cmd, *shlex.split(OPTIONS), *shlex.split(SRC)],
        stdout=PIPE,
        stderr=STDOUT,
        encoding="utf-8",
    )
shutil.rmtree(ENV_PATH, ignore_errors=True)
print(proc.stdout)
sys.exit(proc.returncode)
