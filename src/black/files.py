import io
import operator
import os
import re
import sys
from enum import Enum
from functools import lru_cache, reduce
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Pattern,
    Sequence,
    Tuple,
    Union,
)

from mypy_extensions import mypyc_attr
from packaging.specifiers import InvalidSpecifier, Specifier, SpecifierSet
from packaging.version import InvalidVersion, Version
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPatternError

if sys.version_info >= (3, 11):
    try:
        import tomllib
    except ImportError:
        # Help users on older alphas
        if not TYPE_CHECKING:
            import tomli as tomllib
else:
    import tomli as tomllib

from black.handle_ipynb_magics import jupyter_dependencies_are_installed
from black.mode import TargetVersion
from black.output import err
from black.report import Report

if TYPE_CHECKING:
    import colorama  # noqa: F401


@lru_cache()
def find_project_root(
    srcs: Sequence[str], stdin_filename: Optional[str] = None
) -> Tuple[Path, str]:
    """Return a directory containing .git, .hg, or pyproject.toml.

    That directory will be a common parent of all files and directories
    passed in `srcs`.

    If no directory in the tree contains a marker that would specify it's the
    project root, the root of the file system is returned.

    Returns a two-tuple with the first element as the project root path and
    the second element as a string describing the method by which the
    project root was discovered.
    """
    if stdin_filename is not None:
        srcs = tuple(stdin_filename if s == "-" else s for s in srcs)
    if not srcs:
        srcs = [str(Path.cwd().resolve())]

    path_srcs = [Path(Path.cwd(), src).resolve() for src in srcs]

    # A list of lists of parents for each 'src'. 'src' is included as a
    # "parent" of itself if it is a directory
    src_parents = [
        list(path.parents) + ([path] if path.is_dir() else []) for path in path_srcs
    ]

    common_base = max(
        set.intersection(*(set(parents) for parents in src_parents)),
        key=lambda path: path.parts,
    )

    for directory in (common_base, *common_base.parents):
        if (directory / ".git").exists():
            return directory, ".git directory"

        if (directory / ".hg").is_dir():
            return directory, ".hg directory"

        if (directory / "pyproject.toml").is_file():
            return directory, "pyproject.toml"

    return directory, "file system root"


def find_pyproject_toml(path_search_start: Tuple[str, ...]) -> Optional[str]:
    """Find the absolute filepath to a pyproject.toml if it exists"""
    path_project_root, _ = find_project_root(path_search_start)
    path_pyproject_toml = path_project_root / "pyproject.toml"
    if path_pyproject_toml.is_file():
        return str(path_pyproject_toml)

    try:
        path_user_pyproject_toml = find_user_pyproject_toml()
        return (
            str(path_user_pyproject_toml)
            if path_user_pyproject_toml.is_file()
            else None
        )
    except (PermissionError, RuntimeError) as e:
        # We do not have access to the user-level config directory, so ignore it.
        err(f"Ignoring user configuration directory due to {e!r}")
        return None


@mypyc_attr(patchable=True)
def parse_pyproject_toml(path_config: str) -> Dict[str, Any]:
    """Parse a pyproject toml file, pulling out relevant parts for Black.

    If parsing fails, will raise a tomllib.TOMLDecodeError.
    """
    with open(path_config, "rb") as f:
        pyproject_toml = tomllib.load(f)
    config: Dict[str, Any] = pyproject_toml.get("tool", {}).get("black", {})
    config = {k.replace("--", "").replace("-", "_"): v for k, v in config.items()}

    if "target_version" not in config:
        inferred_target_version = infer_target_version(pyproject_toml)
        if inferred_target_version is not None:
            config["target_version"] = [v.name.lower() for v in inferred_target_version]

    return config


def infer_target_version(
    pyproject_toml: Dict[str, Any]
) -> Optional[List[TargetVersion]]:
    """Infer Black's target version from the project metadata in pyproject.toml.

    Supports the PyPA standard format (PEP 621):
    https://packaging.python.org/en/latest/specifications/declaring-project-metadata/#requires-python

    If the target version cannot be inferred, returns None.
    """
    project_metadata = pyproject_toml.get("project", {})
    requires_python = project_metadata.get("requires-python", None)
    if requires_python is not None:
        try:
            return parse_req_python_version(requires_python)
        except InvalidVersion:
            pass
        try:
            return parse_req_python_specifier(requires_python)
        except (InvalidSpecifier, InvalidVersion):
            pass

    return None


def parse_req_python_version(requires_python: str) -> Optional[List[TargetVersion]]:
    """Parse a version string (i.e. ``"3.7"``) to a list of TargetVersion.

    If parsing fails, will raise a packaging.version.InvalidVersion error.
    If the parsed version cannot be mapped to a valid TargetVersion, returns None.
    """
    version = Version(requires_python)
    if version.release[0] != 3:
        return None
    try:
        return [TargetVersion(version.release[1])]
    except (IndexError, ValueError):
        return None


class Endpoint(Enum):
    CLOSED = 1
    OPEN = 2


CLOSED = Endpoint.CLOSED
OPEN = Endpoint.OPEN


class Interval:
    def __init__(self, left: Endpoint, lower: Any, upper: Any, right: Endpoint):
        if not (lower < upper or (lower == upper and left == right == CLOSED)):
            raise ValueError("empty interval")
        self.left = left
        self.lower = lower
        self.upper = upper
        self.right = right


class IntervalSet:
    """Represents a union of intervals."""

    def __init__(self, intervals: List[Any]):
        self.intervals = intervals

    def __and__(self, other: "IntervalSet") -> "IntervalSet":
        new_intervals = []
        for i1 in self.intervals:
            for i2 in other.intervals:
                if i1.lower < i2.lower:
                    lower = i2.lower
                    left = i2.left
                elif i2.lower < i1.lower:
                    lower = i1.lower
                    left = i1.left
                else:
                    lower = i1.lower
                    left = CLOSED if i1.left == i2.left == CLOSED else OPEN
                if i1.upper < i2.upper:
                    upper = i1.upper
                    right = i1.right
                elif i2.upper < i1.upper:
                    upper = i2.upper
                    right = i2.right
                else:
                    upper = i1.upper
                    right = CLOSED if i1.right == i2.right == CLOSED else OPEN
                try:
                    new_intervals.append(Interval(left, lower, upper, right))
                except ValueError:
                    pass
        return IntervalSet(new_intervals)

    def __or__(self, other: "IntervalSet") -> "IntervalSet":
        return IntervalSet(self.intervals + other.intervals)

    @property
    def empty(self) -> bool:
        return len(self.intervals) == 0


def interval(left: Endpoint, lower: Any, upper: Any, right: Endpoint) -> IntervalSet:
    try:
        return IntervalSet([Interval(left, lower, upper, right)])
    except ValueError:
        return empty


def singleton(value: Any) -> IntervalSet:
    return interval(CLOSED, value, value, CLOSED)


empty = IntervalSet([])
min_ver = Version(f"3.{tuple(TargetVersion)[0].value}")
above_max_ver = Version(f"3.{tuple(TargetVersion)[-1].value + 1}")


def get_interval_set(specifier: Specifier) -> IntervalSet:
    if specifier.version.endswith(".*"):
        assert specifier.operator in ("==", "!=")
        wildcard = True
        ver = Version(specifier.version[:-2])
    else:
        wildcard = False
        if specifier.operator != "===":
            ver = Version(specifier.version)

    if specifier.operator == ">=":
        return interval(CLOSED, ver, above_max_ver, OPEN)
    if specifier.operator == ">":
        return interval(OPEN, ver, above_max_ver, OPEN)
    if specifier.operator == "<=":
        return interval(CLOSED, min_ver, ver, CLOSED)
    if specifier.operator == "<":
        return interval(CLOSED, min_ver, ver, OPEN)
    if specifier.operator == "==":
        if wildcard:
            return interval(
                CLOSED,
                ver,
                Version(".".join(map(str, (*ver.release[:-1], ver.release[-1] + 1)))),
                OPEN,
            )
        else:
            return singleton(ver)
    if specifier.operator == "!=":
        if wildcard:
            return interval(CLOSED, min_ver, ver, OPEN) | interval(
                CLOSED,
                Version(".".join(map(str, (*ver.release[:-1], ver.release[-1] + 1)))),
                above_max_ver,
                OPEN,
            )
        else:
            return interval(CLOSED, min_ver, ver, OPEN) | interval(
                OPEN, ver, above_max_ver, OPEN
            )
    if specifier.operator == "~=":
        return interval(
            CLOSED,
            ver,
            Version(".".join(map(str, (*ver.release[:-2], ver.release[-2] + 1)))),
            OPEN,
        )
    if specifier.operator == "===":
        # This operator should do a simple string equality test. Pip compares
        # it with "X.Y.Z", so only if the version in the specifier is in this
        # exact format, it has a chance to match.
        if re.fullmatch(r"\d+\.\d+\.\d+", specifier.version):
            return singleton(Version(specifier.version))
        else:
            return empty
    raise AssertionError()  # pragma: no cover


def parse_req_python_specifier(requires_python: str) -> Optional[List[TargetVersion]]:
    """Parse a specifier string (i.e. ``">=3.7,<3.10"``) to a list of TargetVersion.

    If parsing fails, will raise a packaging.specifiers.InvalidSpecifier error.
    If the parsed specifier is empty or cannot be mapped to a valid TargetVersion,
    returns None.
    """
    specifier_set = SpecifierSet(requires_python)
    if not specifier_set:
        # This means that the specifier has no version clauses. Technically,
        # all Python versions are included in this specifier. But because the
        # user didn't refer to any specific Python version, we fall back to
        # per-file auto-detection.
        return None

    # First, we determine the version interval set from the specifier set (the
    # clauses in the specifier set are connected by the logical and operator).
    # Then, for each supported Python (minor) version, we check whether the
    # interval set intersects with the interval for this Python version.
    spec_intervals = reduce(
        operator.and_,
        map(get_interval_set, specifier_set),
        interval(CLOSED, min_ver, above_max_ver, OPEN),
    )
    target_versions = [
        tv
        for tv in TargetVersion
        if not (spec_intervals & get_interval_set(Specifier(f"==3.{tv.value}.*"))).empty
    ]
    if not target_versions:
        return None
    else:
        return target_versions


@lru_cache()
def find_user_pyproject_toml() -> Path:
    r"""Return the path to the top-level user configuration for black.

    This looks for ~\.black on Windows and ~/.config/black on Linux and other
    Unix systems.

    May raise:
    - RuntimeError: if the current user has no homedir
    - PermissionError: if the current process cannot access the user's homedir
    """
    if sys.platform == "win32":
        # Windows
        user_config_path = Path.home() / ".black"
    else:
        config_root = os.environ.get("XDG_CONFIG_HOME", "~/.config")
        user_config_path = Path(config_root).expanduser() / "black"
    return user_config_path.resolve()


@lru_cache()
def get_gitignore(root: Path) -> PathSpec:
    """Return a PathSpec matching gitignore content if present."""
    gitignore = root / ".gitignore"
    lines: List[str] = []
    if gitignore.is_file():
        with gitignore.open(encoding="utf-8") as gf:
            lines = gf.readlines()
    try:
        return PathSpec.from_lines("gitwildmatch", lines)
    except GitWildMatchPatternError as e:
        err(f"Could not parse {gitignore}: {e}")
        raise


def normalize_path_maybe_ignore(
    path: Path,
    root: Path,
    report: Optional[Report] = None,
) -> Optional[str]:
    """Normalize `path`. May return `None` if `path` was ignored.

    `report` is where "path ignored" output goes.
    """
    try:
        abspath = path if path.is_absolute() else Path.cwd() / path
        normalized_path = abspath.resolve()
        try:
            root_relative_path = normalized_path.relative_to(root).as_posix()
        except ValueError:
            if report:
                report.path_ignored(
                    path, f"is a symbolic link that points outside {root}"
                )
            return None

    except OSError as e:
        if report:
            report.path_ignored(path, f"cannot be read because {e}")
        return None

    return root_relative_path


def path_is_ignored(
    path: Path, gitignore_dict: Dict[Path, PathSpec], report: Report
) -> bool:
    for gitignore_path, pattern in gitignore_dict.items():
        relative_path = normalize_path_maybe_ignore(path, gitignore_path, report)
        if relative_path is None:
            break
        if pattern.match_file(relative_path):
            report.path_ignored(path, "matches a .gitignore file content")
            return True
    return False


def path_is_excluded(
    normalized_path: str,
    pattern: Optional[Pattern[str]],
) -> bool:
    match = pattern.search(normalized_path) if pattern else None
    return bool(match and match.group(0))


def gen_python_files(
    paths: Iterable[Path],
    root: Path,
    include: Pattern[str],
    exclude: Pattern[str],
    extend_exclude: Optional[Pattern[str]],
    force_exclude: Optional[Pattern[str]],
    report: Report,
    gitignore_dict: Optional[Dict[Path, PathSpec]],
    *,
    verbose: bool,
    quiet: bool,
) -> Iterator[Path]:
    """Generate all files under `path` whose paths are not excluded by the
    `exclude_regex`, `extend_exclude`, or `force_exclude` regexes,
    but are included by the `include` regex.

    Symbolic links pointing outside of the `root` directory are ignored.

    `report` is where output about exclusions goes.
    """

    assert root.is_absolute(), f"INTERNAL ERROR: `root` must be absolute but is {root}"
    for child in paths:
        normalized_path = normalize_path_maybe_ignore(child, root, report)
        if normalized_path is None:
            continue

        # First ignore files matching .gitignore, if passed
        if gitignore_dict and path_is_ignored(child, gitignore_dict, report):
            continue

        # Then ignore with `--exclude` `--extend-exclude` and `--force-exclude` options.
        normalized_path = "/" + normalized_path
        if child.is_dir():
            normalized_path += "/"

        if path_is_excluded(normalized_path, exclude):
            report.path_ignored(child, "matches the --exclude regular expression")
            continue

        if path_is_excluded(normalized_path, extend_exclude):
            report.path_ignored(
                child, "matches the --extend-exclude regular expression"
            )
            continue

        if path_is_excluded(normalized_path, force_exclude):
            report.path_ignored(child, "matches the --force-exclude regular expression")
            continue

        if child.is_dir():
            # If gitignore is None, gitignore usage is disabled, while a Falsey
            # gitignore is when the directory doesn't have a .gitignore file.
            if gitignore_dict is not None:
                new_gitignore_dict = {
                    **gitignore_dict,
                    root / child: get_gitignore(child),
                }
            else:
                new_gitignore_dict = None
            yield from gen_python_files(
                child.iterdir(),
                root,
                include,
                exclude,
                extend_exclude,
                force_exclude,
                report,
                new_gitignore_dict,
                verbose=verbose,
                quiet=quiet,
            )

        elif child.is_file():
            if child.suffix == ".ipynb" and not jupyter_dependencies_are_installed(
                verbose=verbose, quiet=quiet
            ):
                continue
            include_match = include.search(normalized_path) if include else True
            if include_match:
                yield child


def wrap_stream_for_windows(
    f: io.TextIOWrapper,
) -> Union[io.TextIOWrapper, "colorama.AnsiToWin32"]:
    """
    Wrap stream with colorama's wrap_stream so colors are shown on Windows.

    If `colorama` is unavailable, the original stream is returned unmodified.
    Otherwise, the `wrap_stream()` function determines whether the stream needs
    to be wrapped for a Windows environment and will accordingly either return
    an `AnsiToWin32` wrapper or the original stream.
    """
    try:
        from colorama.initialise import wrap_stream
    except ImportError:
        return f
    else:
        # Set `strip=False` to avoid needing to modify test_express_diff_with_color.
        return wrap_stream(f, convert=None, strip=False, autoreset=False, wrap=True)
