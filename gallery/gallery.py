import json
import subprocess
import sys
import tarfile
import zipfile
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, NamedTuple, Optional, Union, cast
from urllib.request import urlopen, urlretrieve

PYPI_INSTANCE = "https://pypi.org/pypi"

ArchiveKind = Union[tarfile.TarFile, zipfile.ZipFile]


class BlackVersion(NamedTuple):
    version: str
    config: Optional[str] = None


def get_pypi_download_url(package: str, version: Optional[str]) -> str:
    with urlopen(PYPI_INSTANCE + f"/{package}/json") as page:
        metadata = json.load(page)

    if version is None:
        sources = metadata["urls"]
    else:
        if version in metadata["releases"]:
            sources = metadata["releases"][version]
        else:
            raise ValueError(
                f"No releases found with given version ('{version}') tag. "
                f"Releases: {metadata['releases'].keys()}"
            )

    for source in sources:
        if source["python_version"] == "source":
            break
    else:
        raise ValueError(f"Couldn't find any sources for {package}")

    return cast(str, source["url"])


def get_package_source(package: str, version: Optional[str]) -> str:
    if package == "cpython":
        if version is None:
            version = "master"
        return f"https://github.com/python/cpython/archive/{version}.zip"
    elif package == "pypy":
        if version is None:
            version = "branch/default"
        return (
            f"https://foss.heptapod.net/pypy/pypy/repository/{version}/archive.tar.bz2"
        )
    else:
        return get_pypi_download_url(package, version)


def get_archive_manager(local_file: str) -> ArchiveKind:
    if tarfile.is_tarfile(local_file):
        return tarfile.open(local_file)
    elif zipfile.is_zipfile(local_file):
        return zipfile.ZipFile(local_file)
    else:
        raise ValueError("Unknown archive kind.")


def get_first_archive_member(archive: ArchiveKind) -> str:
    if isinstance(archive, tarfile.TarFile):
        return archive.getnames()[0]
    elif isinstance(archive, zipfile.ZipFile):
        return archive.namelist()[0]


def download_and_extract(package: str, version: Optional[str], directory: Path) -> Path:
    source = get_package_source(package, version)

    local_file, _ = urlretrieve(source, directory / f"{package}-src")
    with get_archive_manager(local_file) as archive:
        archive.extractall(path=directory)
        result_dir = get_first_archive_member(archive)
    return directory / result_dir


def git_create_repository(repo: Path) -> None:
    subprocess.run(["git", "init"], cwd=repo)
    git_add_and_commit(msg="Inital commit", repo=repo)


def git_add_and_commit(msg: str, repo: Path) -> None:
    subprocess.run(["git", "add", "."], cwd=repo)
    subprocess.run(["git", "commit", "-m", msg, "--allow-empty"], cwd=repo)


def git_switch_branch(
    branch: str, repo: Path, new: bool = False, from_branch: Optional[str] = None
) -> None:
    args = ["git", "checkout"]
    if new:
        args.append("-b")
    args.append(branch)
    if from_branch:
        args.append(from_branch)
    subprocess.run(args, cwd=repo)


def init_repo(options: Namespace) -> Path:
    options.output.mkdir(exist_ok=True)

    source_directory = download_and_extract(
        package=options.pypi_package, version=options.version, directory=options.output
    )
    git_create_repository(source_directory)
    return source_directory


def format_repo_with_version(
    repo: Path,
    from_branch: Optional[str],
    black_repo: Path,
    black_version: BlackVersion,
    input_directory: Path,
) -> str:
    current_branch = f"black-{black_version.version}"
    git_switch_branch(black_version.version, repo=black_repo)
    git_switch_branch(current_branch, repo=repo, new=True, from_branch=from_branch)

    formatter: List[Union[Path, str]] = [
        sys.executable,
        (black_repo / "black.py").resolve(),
        ".",
    ]
    if black_version.config:
        formatter.extend(["--config", input_directory / black_version.config])
    subprocess.run(formatter, cwd=repo)
    git_add_and_commit(f"Format with black v{black_version.version}", repo=repo)

    return current_branch


def format_repo(repo: Path, options: Namespace) -> None:
    black_versions = (BlackVersion(*version.split(":")) for version in options.versions)

    from_branch = None
    for black_version in black_versions:
        from_branch = format_repo_with_version(
            repo=repo,
            from_branch=from_branch,
            black_repo=options.black_repo,
            black_version=black_version,
            input_directory=options.input,
        )
    git_switch_branch("master", repo=repo)
    git_switch_branch("master", repo=options.black_repo)


def main() -> None:
    parser = ArgumentParser()

    parser.add_argument(
        "-p", "--pypi-package", help="PyPI package to download", required=True
    )
    parser.add_argument(
        "-b", "--black-repo", help="Black's git repository", type=Path, required=True
    )
    parser.add_argument(
        "-v", "--version", help="Version for PyPI package", default=None
    )
    parser.add_argument(
        "-i",
        "--input",
        default=Path("/input"),
        help="Input directory to read pyproject.toml's from",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=Path("/output"),
        help="Output directory to download packages",
    )
    parser.add_argument("versions", nargs="*", default=("master",), help="")

    options = parser.parse_args()
    repo = init_repo(options)
    format_repo(repo, options)


if __name__ == "__main__":
    main()
