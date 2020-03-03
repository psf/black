#!/usr/bin/env python3
from typing import List, Optional

import argparse
import re
import pathlib
import subprocess

from virtualenv import cli_run

# https://www.regexmagic.com/manual.html#xmpversion
VERSION_RE = re.compile(
    r"\bv?(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<release>[0-9]+)(?:\.(?P<build>[0-9]+))?\b"
)


def version_regex(arg_value: str) -> str:
    if not VERSION_RE.match(arg_value):
        raise argparse.ArgumentTypeError
    return arg_value


def download_package(
    package: str, version: Optional[str], path: pathlib.Path
) -> List[pathlib.Path]:
    p = subprocess.Popen(["git", "init", str(path)], cwd=str(path))
    p.wait()
    if version is None:
        package = f"{package}=={version}"
    p = subprocess.Popen(
        ["pip", "download", package, "--no-deps", "--dest", str(path)], cwd=str(path)
    )
    p.wait()
    package_whl = list(
        filter(lambda i: package.lower() in str(i).lower(), sorted(path.glob("*.whl")))
    )[0]
    p = subprocess.Popen(["wheel", "unpack", str(package_whl), "--dest", str(path)])
    p.wait()

    top_level = list(path.glob("*/*.dist-info/top_level.txt"))[0]
    with open(top_level) as tl:
        packages = tl.read().splitlines()
    package_paths = [
        subchild
        for child in path.iterdir()
        if child.is_dir()
        for subchild in child.iterdir()
        if (str(subchild.name) in packages)
    ]

    p = subprocess.Popen(["git", "add", *package_paths], cwd=str(path))
    p.wait()
    p = subprocess.Popen(
        ["git", "config", "user.email", "black@psf.org"], cwd=str(path)
    )
    p.wait()
    p = subprocess.Popen(["git", "commit", "-m", "Initial commit"], cwd=str(path))
    p.wait()
    return package_paths


def cleanup_path(path: pathlib.Path) -> None:
    for child in path.iterdir():
        if child.is_dir():
            cleanup_path(child)
            child.rmdir()
        else:
            child.unlink()


def install_black(version: str, path: pathlib.Path, *packages: pathlib.Path) -> None:
    venv_path = path / f"venv-{version}"
    cli_run([str(venv_path)])
    p = subprocess.Popen([f"{venv_path}/bin/pip", "install", f"black=={version}"])
    p.wait()
    p = subprocess.Popen(["git", "checkout", "-b", f"black-{version}"], cwd=str(path))
    p.wait()
    p = subprocess.Popen([f"{venv_path}/bin/black", *packages])
    p.wait()
    p = subprocess.Popen(["git", "add", "-u"], cwd=str(path))
    p.wait()
    p = subprocess.Popen(["git", "commit", "-m", f"black-{version}"], cwd=str(path))
    p.wait()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", dest="package", help="PYPI package")
    parser.add_argument("-v", dest="version", default=None, help="PYPI package version")
    parser.add_argument(
        "blacks", metavar="VERSION", type=str, nargs="+", help="black version(s)",
    )
    args = parser.parse_args()

    path = pathlib.Path("/output")
    cleanup_path(path)
    path.mkdir(exist_ok=True)
    packages = download_package(args.package, args.version, path)
    for black_version in args.blacks:
        install_black(black_version, path, *packages)
    print("done!")


if __name__ == "__main__":
    main()
