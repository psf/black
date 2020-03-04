#!/usr/bin/env python3
from typing import List, Optional

import argparse
from pathlib import Path
import re
import subprocess

from virtualenv import cli_run  # type: ignore

# https://www.regexmagic.com/manual.html#xmpversion
VERSION_RE = re.compile(
    r"\bv?(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<release>[0-9]+)(?:\.(?P<build>[0-9]+))?\b"
)


def version_regex(arg_value: str) -> str:
    if not VERSION_RE.match(arg_value):
        raise argparse.ArgumentTypeError
    return arg_value


def _find_package_folders(path: Path) -> List[Path]:
    top_level = list(path.glob("*.dist-info/top_level.txt"))[0]

    with open(top_level) as tl:
        package_names = tl.read().splitlines()

    packages = [child for child in path.iterdir() if child.name in package_names]
    return packages


def download_package(package: str, version: Optional[str], path: Path) -> List[Path]:
    if version is None:
        package = f"{package}=={version}"

    subprocess.run(["pip", "install", package, "--no-deps", "--target", path], cwd=path)

    # TODO: delete all meta folders and files
    return _find_package_folders(path)


def cleanup_path(path: Path) -> None:
    for child in path.iterdir():
        if child.is_dir():
            cleanup_path(child)
            child.rmdir()
        else:
            child.unlink()


def git_init(path: Path, packages: List[Path]) -> None:
    subprocess.run(["git", "init", path], cwd=path)
    subprocess.run(["git", "add", *packages], cwd=path)
    subprocess.run(["git", "config", "user.email", "black@psf.org"], cwd=path)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=path)


def git_create_branch(branch: str, path: Path) -> None:
    subprocess.run(["git", "checkout", "-b", branch], cwd=path)


def git_commit(message: str, path: Path) -> None:
    subprocess.run(["git", "add", "-u"], cwd=path)
    subprocess.run(["git", "commit", "-m", message], cwd=path)


def install_black(version: str, path: Path, *packages: Path) -> None:
    venv_path = path / f"venv-{version}"
    cli_run([str(venv_path)])
    subprocess.run([f"{venv_path}/bin/pip", "install", f"black=={version}"])
    git_create_branch(f"black-{version}", path)
    subprocess.run([f"{venv_path}/bin/black", *packages])
    git_commit(f"black-{version}", path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", dest="package", help="PYPI package")
    parser.add_argument("-v", dest="version", default=None, help="PYPI package version")
    parser.add_argument(
        "blacks", metavar="VERSION", type=str, nargs="+", help="black version(s)",
    )
    args = parser.parse_args()

    path = Path("/output")
    cleanup_path(path)
    path.mkdir(exist_ok=True)
    packages = download_package(args.package, args.version, path)
    git_init(path, packages)
    for black_version in args.blacks:
        install_black(black_version, path, *packages)
    print("done!")


if __name__ == "__main__":
    main()
