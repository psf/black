import ast
import asyncio
from abc import ABC, abstractmethod
from collections import defaultdict
from concurrent.futures import Executor, ThreadPoolExecutor, ProcessPoolExecutor
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from functools import lru_cache, partial, wraps
import io
import itertools
import logging
from multiprocessing import Manager, freeze_support
import os
from pathlib import Path
import pickle
import regex as re
import signal
import sys
import tempfile
import tokenize
import traceback
from typing import (
    Any,
    Callable,
    Collection,
    Dict,
    Generator,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Pattern,
    Sequence,
    Set,
    Sized,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    TYPE_CHECKING,
)
from mypy_extensions import mypyc_attr

from appdirs import user_cache_dir
from dataclasses import dataclass, field, replace
import click
import toml

try:
    from typed_ast import ast3, ast27
except ImportError:
    if sys.version_info < (3, 8):
        print(
            "The typed_ast package is not installed.\n"
            "You can install it with `python3 -m pip install typed-ast`.",
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        ast3 = ast27 = ast

from pathspec import PathSpec

# lib2to3 fork
from blib2to3.pytree import Node, Leaf, type_repr
from blib2to3 import pygram, pytree
from blib2to3.pgen2 import driver, token
from blib2to3.pgen2.grammar import Grammar
from blib2to3.pgen2.parse import ParseError

from _black_version import version as __version__

if sys.version_info < (3, 8):
    from typing_extensions import Final
else:
    from typing import Final

if TYPE_CHECKING:
    import colorama  # noqa: F401

DEFAULT_LINE_LENGTH = 88
DEFAULT_EXCLUDES = r"/(\.direnv|\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|venv|\.svn|_build|buck-out|build|dist)/"  # noqa: B950
DEFAULT_INCLUDES = r"\.pyi?$"
CACHE_DIR = Path(user_cache_dir("black", version=__version__))
STDIN_PLACEHOLDER = "__BLACK_STDIN_FILENAME__"

STRING_PREFIX_CHARS: Final = "furbFURB"  # All possible string prefix characters.


# types
FileContent = str
Encoding = str
NewLine = str
Depth = int
NodeType = int
ParserState = int
LeafID = int
StringID = int
Priority = int
Index = int
LN = Union[Leaf, Node]
Transformer = Callable[["Line", Collection["Feature"]], Iterator["Line"]]
Timestamp = float
FileSize = int
CacheInfo = Tuple[Timestamp, FileSize]
Cache = Dict[str, CacheInfo]
out = partial(click.secho, bold=True, err=True)
err = partial(click.secho, fg="red", err=True)

pygram.initialize(CACHE_DIR)
syms = pygram.python_symbols


class NothingChanged(UserWarning):
    """Raised when reformatted code is the same as source."""


class CannotTransform(Exception):
    """Base class for errors raised by Transformers."""


class CannotSplit(CannotTransform):
    """A readable split that fits the allotted line length is impossible."""


class InvalidInput(ValueError):
    """Raised when input source code fails all parse attempts."""


class BracketMatchError(KeyError):
    """Raised when an opening bracket is unable to be matched to a closing bracket."""


T = TypeVar("T")
E = TypeVar("E", bound=Exception)


class Ok(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value = value

    def ok(self) -> T:
        return self._value


class Err(Generic[E]):
    def __init__(self, e: E) -> None:
        self._e = e

    def err(self) -> E:
        return self._e


# The 'Result' return type is used to implement an error-handling model heavily
# influenced by that used by the Rust programming language
# (see https://doc.rust-lang.org/book/ch09-00-error-handling.html).
Result = Union[Ok[T], Err[E]]
TResult = Result[T, CannotTransform]  # (T)ransform Result
TMatchResult = TResult[Index]


class WriteBack(Enum):
    NO = 0
    YES = 1
    DIFF = 2
    CHECK = 3
    COLOR_DIFF = 4

    @classmethod
    def from_configuration(
        cls, *, check: bool, diff: bool, color: bool = False
    ) -> "WriteBack":
        if check and not diff:
            return cls.CHECK

        if diff and color:
            return cls.COLOR_DIFF

        return cls.DIFF if diff else cls.YES


class Changed(Enum):
    NO = 0
    CACHED = 1
    YES = 2


class TargetVersion(Enum):
    PY27 = 2
    PY33 = 3
    PY34 = 4
    PY35 = 5
    PY36 = 6
    PY37 = 7
    PY38 = 8
    PY39 = 9

    def is_python2(self) -> bool:
        return self is TargetVersion.PY27


class Feature(Enum):
    # All string literals are unicode
    UNICODE_LITERALS = 1
    F_STRINGS = 2
    NUMERIC_UNDERSCORES = 3
    TRAILING_COMMA_IN_CALL = 4
    TRAILING_COMMA_IN_DEF = 5
    # The following two feature-flags are mutually exclusive, and exactly one should be
    # set for every version of python.
    ASYNC_IDENTIFIERS = 6
    ASYNC_KEYWORDS = 7
    ASSIGNMENT_EXPRESSIONS = 8
    POS_ONLY_ARGUMENTS = 9
    RELAXED_DECORATORS = 10
    FORCE_OPTIONAL_PARENTHESES = 50


VERSION_TO_FEATURES: Dict[TargetVersion, Set[Feature]] = {
    TargetVersion.PY27: {Feature.ASYNC_IDENTIFIERS},
    TargetVersion.PY33: {Feature.UNICODE_LITERALS, Feature.ASYNC_IDENTIFIERS},
    TargetVersion.PY34: {Feature.UNICODE_LITERALS, Feature.ASYNC_IDENTIFIERS},
    TargetVersion.PY35: {
        Feature.UNICODE_LITERALS,
        Feature.TRAILING_COMMA_IN_CALL,
        Feature.ASYNC_IDENTIFIERS,
    },
    TargetVersion.PY36: {
        Feature.UNICODE_LITERALS,
        Feature.F_STRINGS,
        Feature.NUMERIC_UNDERSCORES,
        Feature.TRAILING_COMMA_IN_CALL,
        Feature.TRAILING_COMMA_IN_DEF,
        Feature.ASYNC_IDENTIFIERS,
    },
    TargetVersion.PY37: {
        Feature.UNICODE_LITERALS,
        Feature.F_STRINGS,
        Feature.NUMERIC_UNDERSCORES,
        Feature.TRAILING_COMMA_IN_CALL,
        Feature.TRAILING_COMMA_IN_DEF,
        Feature.ASYNC_KEYWORDS,
    },
    TargetVersion.PY38: {
        Feature.UNICODE_LITERALS,
        Feature.F_STRINGS,
        Feature.NUMERIC_UNDERSCORES,
        Feature.TRAILING_COMMA_IN_CALL,
        Feature.TRAILING_COMMA_IN_DEF,
        Feature.ASYNC_KEYWORDS,
        Feature.ASSIGNMENT_EXPRESSIONS,
        Feature.POS_ONLY_ARGUMENTS,
    },
    TargetVersion.PY39: {
        Feature.UNICODE_LITERALS,
        Feature.F_STRINGS,
        Feature.NUMERIC_UNDERSCORES,
        Feature.TRAILING_COMMA_IN_CALL,
        Feature.TRAILING_COMMA_IN_DEF,
        Feature.ASYNC_KEYWORDS,
        Feature.ASSIGNMENT_EXPRESSIONS,
        Feature.RELAXED_DECORATORS,
        Feature.POS_ONLY_ARGUMENTS,
    },
}


@dataclass
class Mode:
    target_versions: Set[TargetVersion] = field(default_factory=set)
    line_length: int = DEFAULT_LINE_LENGTH
    string_normalization: bool = True
    is_pyi: bool = False
    magic_trailing_comma: bool = True
    experimental_string_processing: bool = False

    def get_cache_key(self) -> str:
        if self.target_versions:
            version_str = ",".join(
                str(version.value)
                for version in sorted(self.target_versions, key=lambda v: v.value)
            )
        else:
            version_str = "-"
        parts = [
            version_str,
            str(self.line_length),
            str(int(self.string_normalization)),
            str(int(self.is_pyi)),
            str(int(self.magic_trailing_comma)),
            str(int(self.experimental_string_processing)),
        ]
        return ".".join(parts)


# Legacy name, left for integrations.
FileMode = Mode


def supports_feature(target_versions: Set[TargetVersion], feature: Feature) -> bool:
    return all(feature in VERSION_TO_FEATURES[version] for version in target_versions)


def find_pyproject_toml(path_search_start: Tuple[str, ...]) -> Optional[str]:
    """Find the absolute filepath to a pyproject.toml if it exists"""
    path_project_root = find_project_root(path_search_start)
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
    except PermissionError as e:
        # We do not have access to the user-level config directory, so ignore it.
        err(f"Ignoring user configuration directory due to {e!r}")
        return None


def parse_pyproject_toml(path_config: str) -> Dict[str, Any]:
    """Parse a pyproject toml file, pulling out relevant parts for Black

    If parsing fails, will raise a toml.TomlDecodeError
    """
    pyproject_toml = toml.load(path_config)
    config = pyproject_toml.get("tool", {}).get("black", {})
    return {k.replace("--", "").replace("-", "_"): v for k, v in config.items()}


def read_pyproject_toml(
    ctx: click.Context, param: click.Parameter, value: Optional[str]
) -> Optional[str]:
    """Inject Black configuration from "pyproject.toml" into defaults in `ctx`.

    Returns the path to a successfully found and read configuration file, None
    otherwise.
    """
    if not value:
        value = find_pyproject_toml(ctx.params.get("src", ()))
        if value is None:
            return None

    try:
        config = parse_pyproject_toml(value)
    except (toml.TomlDecodeError, OSError) as e:
        raise click.FileError(
            filename=value, hint=f"Error reading configuration file: {e}"
        )

    if not config:
        return None
    else:
        # Sanitize the values to be Click friendly. For more information please see:
        # https://github.com/psf/black/issues/1458
        # https://github.com/pallets/click/issues/1567
        config = {
            k: str(v) if not isinstance(v, (list, dict)) else v
            for k, v in config.items()
        }

    target_version = config.get("target_version")
    if target_version is not None and not isinstance(target_version, list):
        raise click.BadOptionUsage(
            "target-version", "Config key target-version must be a list"
        )

    default_map: Dict[str, Any] = {}
    if ctx.default_map:
        default_map.update(ctx.default_map)
    default_map.update(config)

    ctx.default_map = default_map
    return value


def target_version_option_callback(
    c: click.Context, p: Union[click.Option, click.Parameter], v: Tuple[str, ...]
) -> List[TargetVersion]:
    """Compute the target versions from a --target-version flag.

    This is its own function because mypy couldn't infer the type correctly
    when it was a lambda, causing mypyc trouble.
    """
    return [TargetVersion[val.upper()] for val in v]


def validate_regex(
    ctx: click.Context,
    param: click.Parameter,
    value: Optional[str],
) -> Optional[Pattern]:
    try:
        return re_compile_maybe_verbose(value) if value is not None else None
    except re.error:
        raise click.BadParameter("Not a valid regular expression")


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("-c", "--code", type=str, help="Format the code passed in as a string.")
@click.option(
    "-l",
    "--line-length",
    type=int,
    default=DEFAULT_LINE_LENGTH,
    help="How many characters per line to allow.",
    show_default=True,
)
@click.option(
    "-t",
    "--target-version",
    type=click.Choice([v.name.lower() for v in TargetVersion]),
    callback=target_version_option_callback,
    multiple=True,
    help=(
        "Python versions that should be supported by Black's output. [default: per-file"
        " auto-detection]"
    ),
)
@click.option(
    "--pyi",
    is_flag=True,
    help=(
        "Format all input files like typing stubs regardless of file extension (useful"
        " when piping source on standard input)."
    ),
)
@click.option(
    "-S",
    "--skip-string-normalization",
    is_flag=True,
    help="Don't normalize string quotes or prefixes.",
)
@click.option(
    "-C",
    "--skip-magic-trailing-comma",
    is_flag=True,
    help="Don't use trailing commas as a reason to split lines.",
)
@click.option(
    "--experimental-string-processing",
    is_flag=True,
    hidden=True,
    help=(
        "Experimental option that performs more normalization on string literals."
        " Currently disabled because it leads to some crashes."
    ),
)
@click.option(
    "--check",
    is_flag=True,
    help=(
        "Don't write the files back, just return the status. Return code 0 means"
        " nothing would change. Return code 1 means some files would be reformatted."
        " Return code 123 means there was an internal error."
    ),
)
@click.option(
    "--diff",
    is_flag=True,
    help="Don't write the files back, just output a diff for each file on stdout.",
)
@click.option(
    "--color/--no-color",
    is_flag=True,
    help="Show colored diff. Only applies when `--diff` is given.",
)
@click.option(
    "--fast/--safe",
    is_flag=True,
    help="If --fast given, skip temporary sanity checks. [default: --safe]",
)
@click.option(
    "--include",
    type=str,
    default=DEFAULT_INCLUDES,
    callback=validate_regex,
    help=(
        "A regular expression that matches files and directories that should be"
        " included on recursive searches. An empty value means all files are included"
        " regardless of the name. Use forward slashes for directories on all platforms"
        " (Windows, too). Exclusions are calculated first, inclusions later."
    ),
    show_default=True,
)
@click.option(
    "--exclude",
    type=str,
    default=DEFAULT_EXCLUDES,
    callback=validate_regex,
    help=(
        "A regular expression that matches files and directories that should be"
        " excluded on recursive searches. An empty value means no paths are excluded."
        " Use forward slashes for directories on all platforms (Windows, too)."
        " Exclusions are calculated first, inclusions later."
    ),
    show_default=True,
)
@click.option(
    "--extend-exclude",
    type=str,
    callback=validate_regex,
    help=(
        "Like --exclude, but adds additional files and directories on top of the"
        " excluded ones. (Useful if you simply want to add to the default)"
    ),
)
@click.option(
    "--force-exclude",
    type=str,
    callback=validate_regex,
    help=(
        "Like --exclude, but files and directories matching this regex will be "
        "excluded even when they are passed explicitly as arguments."
    ),
)
@click.option(
    "--stdin-filename",
    type=str,
    help=(
        "The name of the file when passing it through stdin. Useful to make "
        "sure Black will respect --force-exclude option on some "
        "editors that rely on using stdin."
    ),
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help=(
        "Don't emit non-error messages to stderr. Errors are still emitted; silence"
        " those with 2>/dev/null."
    ),
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help=(
        "Also emit messages to stderr about files that were not changed or were ignored"
        " due to exclusion patterns."
    ),
)
@click.version_option(version=__version__)
@click.argument(
    "src",
    nargs=-1,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, readable=True, allow_dash=True
    ),
    is_eager=True,
)
@click.option(
    "--config",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        allow_dash=False,
        path_type=str,
    ),
    is_eager=True,
    callback=read_pyproject_toml,
    help="Read configuration from FILE path.",
)
@click.pass_context
def main(
    ctx: click.Context,
    code: Optional[str],
    line_length: int,
    target_version: List[TargetVersion],
    check: bool,
    diff: bool,
    color: bool,
    fast: bool,
    pyi: bool,
    skip_string_normalization: bool,
    skip_magic_trailing_comma: bool,
    experimental_string_processing: bool,
    quiet: bool,
    verbose: bool,
    include: Pattern,
    exclude: Pattern,
    extend_exclude: Optional[Pattern],
    force_exclude: Optional[Pattern],
    stdin_filename: Optional[str],
    src: Tuple[str, ...],
    config: Optional[str],
) -> None:
    """The uncompromising code formatter."""
    write_back = WriteBack.from_configuration(check=check, diff=diff, color=color)
    if target_version:
        versions = set(target_version)
    else:
        # We'll autodetect later.
        versions = set()
    mode = Mode(
        target_versions=versions,
        line_length=line_length,
        is_pyi=pyi,
        string_normalization=not skip_string_normalization,
        magic_trailing_comma=not skip_magic_trailing_comma,
        experimental_string_processing=experimental_string_processing,
    )
    if config and verbose:
        out(f"Using configuration from {config}.", bold=False, fg="blue")
    if code is not None:
        print(format_str(code, mode=mode))
        ctx.exit(0)
    report = Report(check=check, diff=diff, quiet=quiet, verbose=verbose)
    sources = get_sources(
        ctx=ctx,
        src=src,
        quiet=quiet,
        verbose=verbose,
        include=include,
        exclude=exclude,
        extend_exclude=extend_exclude,
        force_exclude=force_exclude,
        report=report,
        stdin_filename=stdin_filename,
    )

    path_empty(
        sources,
        "No Python files are present to be formatted. Nothing to do 😴",
        quiet,
        verbose,
        ctx,
    )

    if len(sources) == 1:
        reformat_one(
            src=sources.pop(),
            fast=fast,
            write_back=write_back,
            mode=mode,
            report=report,
        )
    else:
        reformat_many(
            sources=sources, fast=fast, write_back=write_back, mode=mode, report=report
        )

    if verbose or not quiet:
        out("Oh no! 💥 💔 💥" if report.return_code else "All done! ✨ 🍰 ✨")
        click.secho(str(report), err=True)
    ctx.exit(report.return_code)


def get_sources(
    *,
    ctx: click.Context,
    src: Tuple[str, ...],
    quiet: bool,
    verbose: bool,
    include: Pattern[str],
    exclude: Pattern[str],
    extend_exclude: Optional[Pattern[str]],
    force_exclude: Optional[Pattern[str]],
    report: "Report",
    stdin_filename: Optional[str],
) -> Set[Path]:
    """Compute the set of files to be formatted."""

    root = find_project_root(src)
    sources: Set[Path] = set()
    path_empty(src, "No Path provided. Nothing to do 😴", quiet, verbose, ctx)
    gitignore = get_gitignore(root)

    for s in src:
        if s == "-" and stdin_filename:
            p = Path(stdin_filename)
            is_stdin = True
        else:
            p = Path(s)
            is_stdin = False

        if is_stdin or p.is_file():
            normalized_path = normalize_path_maybe_ignore(p, root, report)
            if normalized_path is None:
                continue

            normalized_path = "/" + normalized_path
            # Hard-exclude any files that matches the `--force-exclude` regex.
            if force_exclude:
                force_exclude_match = force_exclude.search(normalized_path)
            else:
                force_exclude_match = None
            if force_exclude_match and force_exclude_match.group(0):
                report.path_ignored(p, "matches the --force-exclude regular expression")
                continue

            if is_stdin:
                p = Path(f"{STDIN_PLACEHOLDER}{str(p)}")

            sources.add(p)
        elif p.is_dir():
            sources.update(
                gen_python_files(
                    p.iterdir(),
                    root,
                    include,
                    exclude,
                    extend_exclude,
                    force_exclude,
                    report,
                    gitignore,
                )
            )
        elif s == "-":
            sources.add(p)
        else:
            err(f"invalid path: {s}")
    return sources


def path_empty(
    src: Sized, msg: str, quiet: bool, verbose: bool, ctx: click.Context
) -> None:
    """
    Exit if there is no `src` provided for formatting
    """
    if not src and (verbose or not quiet):
        out(msg)
        ctx.exit(0)


def reformat_one(
    src: Path, fast: bool, write_back: WriteBack, mode: Mode, report: "Report"
) -> None:
    """Reformat a single file under `src` without spawning child processes.

    `fast`, `write_back`, and `mode` options are passed to
    :func:`format_file_in_place` or :func:`format_stdin_to_stdout`.
    """
    try:
        changed = Changed.NO

        if str(src) == "-":
            is_stdin = True
        elif str(src).startswith(STDIN_PLACEHOLDER):
            is_stdin = True
            # Use the original name again in case we want to print something
            # to the user
            src = Path(str(src)[len(STDIN_PLACEHOLDER) :])
        else:
            is_stdin = False

        if is_stdin:
            if src.suffix == ".pyi":
                mode = replace(mode, is_pyi=True)
            if format_stdin_to_stdout(fast=fast, write_back=write_back, mode=mode):
                changed = Changed.YES
        else:
            cache: Cache = {}
            if write_back not in (WriteBack.DIFF, WriteBack.COLOR_DIFF):
                cache = read_cache(mode)
                res_src = src.resolve()
                res_src_s = str(res_src)
                if res_src_s in cache and cache[res_src_s] == get_cache_info(res_src):
                    changed = Changed.CACHED
            if changed is not Changed.CACHED and format_file_in_place(
                src, fast=fast, write_back=write_back, mode=mode
            ):
                changed = Changed.YES
            if (write_back is WriteBack.YES and changed is not Changed.CACHED) or (
                write_back is WriteBack.CHECK and changed is Changed.NO
            ):
                write_cache(cache, [src], mode)
        report.done(src, changed)
    except Exception as exc:
        if report.verbose:
            traceback.print_exc()
        report.failed(src, str(exc))


def reformat_many(
    sources: Set[Path], fast: bool, write_back: WriteBack, mode: Mode, report: "Report"
) -> None:
    """Reformat multiple files using a ProcessPoolExecutor."""
    executor: Executor
    loop = asyncio.get_event_loop()
    worker_count = os.cpu_count()
    if sys.platform == "win32":
        # Work around https://bugs.python.org/issue26903
        worker_count = min(worker_count, 60)
    try:
        executor = ProcessPoolExecutor(max_workers=worker_count)
    except (ImportError, OSError):
        # we arrive here if the underlying system does not support multi-processing
        # like in AWS Lambda or Termux, in which case we gracefully fallback to
        # a ThreadPoolExecutor with just a single worker (more workers would not do us
        # any good due to the Global Interpreter Lock)
        executor = ThreadPoolExecutor(max_workers=1)

    try:
        loop.run_until_complete(
            schedule_formatting(
                sources=sources,
                fast=fast,
                write_back=write_back,
                mode=mode,
                report=report,
                loop=loop,
                executor=executor,
            )
        )
    finally:
        shutdown(loop)
        if executor is not None:
            executor.shutdown()


async def schedule_formatting(
    sources: Set[Path],
    fast: bool,
    write_back: WriteBack,
    mode: Mode,
    report: "Report",
    loop: asyncio.AbstractEventLoop,
    executor: Executor,
) -> None:
    """Run formatting of `sources` in parallel using the provided `executor`.

    (Use ProcessPoolExecutors for actual parallelism.)

    `write_back`, `fast`, and `mode` options are passed to
    :func:`format_file_in_place`.
    """
    cache: Cache = {}
    if write_back not in (WriteBack.DIFF, WriteBack.COLOR_DIFF):
        cache = read_cache(mode)
        sources, cached = filter_cached(cache, sources)
        for src in sorted(cached):
            report.done(src, Changed.CACHED)
    if not sources:
        return

    cancelled = []
    sources_to_cache = []
    lock = None
    if write_back in (WriteBack.DIFF, WriteBack.COLOR_DIFF):
        # For diff output, we need locks to ensure we don't interleave output
        # from different processes.
        manager = Manager()
        lock = manager.Lock()
    tasks = {
        asyncio.ensure_future(
            loop.run_in_executor(
                executor, format_file_in_place, src, fast, mode, write_back, lock
            )
        ): src
        for src in sorted(sources)
    }
    pending = tasks.keys()
    try:
        loop.add_signal_handler(signal.SIGINT, cancel, pending)
        loop.add_signal_handler(signal.SIGTERM, cancel, pending)
    except NotImplementedError:
        # There are no good alternatives for these on Windows.
        pass
    while pending:
        done, _ = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            src = tasks.pop(task)
            if task.cancelled():
                cancelled.append(task)
            elif task.exception():
                report.failed(src, str(task.exception()))
            else:
                changed = Changed.YES if task.result() else Changed.NO
                # If the file was written back or was successfully checked as
                # well-formatted, store this information in the cache.
                if write_back is WriteBack.YES or (
                    write_back is WriteBack.CHECK and changed is Changed.NO
                ):
                    sources_to_cache.append(src)
                report.done(src, changed)
    if cancelled:
        await asyncio.gather(*cancelled, loop=loop, return_exceptions=True)
    if sources_to_cache:
        write_cache(cache, sources_to_cache, mode)


def format_file_in_place(
    src: Path,
    fast: bool,
    mode: Mode,
    write_back: WriteBack = WriteBack.NO,
    lock: Any = None,  # multiprocessing.Manager().Lock() is some crazy proxy
) -> bool:
    """Format file under `src` path. Return True if changed.

    If `write_back` is DIFF, write a diff to stdout. If it is YES, write reformatted
    code to the file.
    `mode` and `fast` options are passed to :func:`format_file_contents`.
    """
    if src.suffix == ".pyi":
        mode = replace(mode, is_pyi=True)

    then = datetime.utcfromtimestamp(src.stat().st_mtime)
    with open(src, "rb") as buf:
        src_contents, encoding, newline = decode_bytes(buf.read())
    try:
        dst_contents = format_file_contents(src_contents, fast=fast, mode=mode)
    except NothingChanged:
        return False

    if write_back == WriteBack.YES:
        with open(src, "w", encoding=encoding, newline=newline) as f:
            f.write(dst_contents)
    elif write_back in (WriteBack.DIFF, WriteBack.COLOR_DIFF):
        now = datetime.utcnow()
        src_name = f"{src}\t{then} +0000"
        dst_name = f"{src}\t{now} +0000"
        diff_contents = diff(src_contents, dst_contents, src_name, dst_name)

        if write_back == WriteBack.COLOR_DIFF:
            diff_contents = color_diff(diff_contents)

        with lock or nullcontext():
            f = io.TextIOWrapper(
                sys.stdout.buffer,
                encoding=encoding,
                newline=newline,
                write_through=True,
            )
            f = wrap_stream_for_windows(f)
            f.write(diff_contents)
            f.detach()

    return True


def color_diff(contents: str) -> str:
    """Inject the ANSI color codes to the diff."""
    lines = contents.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("+++") or line.startswith("---"):
            line = "\033[1;37m" + line + "\033[0m"  # bold white, reset
        elif line.startswith("@@"):
            line = "\033[36m" + line + "\033[0m"  # cyan, reset
        elif line.startswith("+"):
            line = "\033[32m" + line + "\033[0m"  # green, reset
        elif line.startswith("-"):
            line = "\033[31m" + line + "\033[0m"  # red, reset
        lines[i] = line
    return "\n".join(lines)


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


def format_stdin_to_stdout(
    fast: bool, *, write_back: WriteBack = WriteBack.NO, mode: Mode
) -> bool:
    """Format file on stdin. Return True if changed.

    If `write_back` is YES, write reformatted code back to stdout. If it is DIFF,
    write a diff to stdout. The `mode` argument is passed to
    :func:`format_file_contents`.
    """
    then = datetime.utcnow()
    src, encoding, newline = decode_bytes(sys.stdin.buffer.read())
    dst = src
    try:
        dst = format_file_contents(src, fast=fast, mode=mode)
        return True

    except NothingChanged:
        return False

    finally:
        f = io.TextIOWrapper(
            sys.stdout.buffer, encoding=encoding, newline=newline, write_through=True
        )
        if write_back == WriteBack.YES:
            f.write(dst)
        elif write_back in (WriteBack.DIFF, WriteBack.COLOR_DIFF):
            now = datetime.utcnow()
            src_name = f"STDIN\t{then} +0000"
            dst_name = f"STDOUT\t{now} +0000"
            d = diff(src, dst, src_name, dst_name)
            if write_back == WriteBack.COLOR_DIFF:
                d = color_diff(d)
                f = wrap_stream_for_windows(f)
            f.write(d)
        f.detach()


def format_file_contents(src_contents: str, *, fast: bool, mode: Mode) -> FileContent:
    """Reformat contents of a file and return new contents.

    If `fast` is False, additionally confirm that the reformatted code is
    valid by calling :func:`assert_equivalent` and :func:`assert_stable` on it.
    `mode` is passed to :func:`format_str`.
    """
    if not src_contents.strip():
        raise NothingChanged

    dst_contents = format_str(src_contents, mode=mode)
    if src_contents == dst_contents:
        raise NothingChanged

    if not fast:
        assert_equivalent(src_contents, dst_contents)

        # Forced second pass to work around optional trailing commas (becoming
        # forced trailing commas on pass 2) interacting differently with optional
        # parentheses.  Admittedly ugly.
        dst_contents_pass2 = format_str(dst_contents, mode=mode)
        if dst_contents != dst_contents_pass2:
            dst_contents = dst_contents_pass2
            assert_equivalent(src_contents, dst_contents, pass_num=2)
            assert_stable(src_contents, dst_contents, mode=mode)
        # Note: no need to explicitly call `assert_stable` if `dst_contents` was
        # the same as `dst_contents_pass2`.
    return dst_contents


def format_str(src_contents: str, *, mode: Mode) -> FileContent:
    """Reformat a string and return new contents.

    `mode` determines formatting options, such as how many characters per line are
    allowed.  Example:

    >>> import black
    >>> print(black.format_str("def f(arg:str='')->None:...", mode=black.Mode()))
    def f(arg: str = "") -> None:
        ...

    A more complex example:

    >>> print(
    ...   black.format_str(
    ...     "def f(arg:str='')->None: hey",
    ...     mode=black.Mode(
    ...       target_versions={black.TargetVersion.PY36},
    ...       line_length=10,
    ...       string_normalization=False,
    ...       is_pyi=False,
    ...     ),
    ...   ),
    ... )
    def f(
        arg: str = '',
    ) -> None:
        hey

    """
    src_node = lib2to3_parse(src_contents.lstrip(), mode.target_versions)
    dst_contents = []
    future_imports = get_future_imports(src_node)
    if mode.target_versions:
        versions = mode.target_versions
    else:
        versions = detect_target_versions(src_node)
    normalize_fmt_off(src_node)
    lines = LineGenerator(
        mode=mode,
        remove_u_prefix="unicode_literals" in future_imports
        or supports_feature(versions, Feature.UNICODE_LITERALS),
    )
    elt = EmptyLineTracker(is_pyi=mode.is_pyi)
    empty_line = Line(mode=mode)
    after = 0
    split_line_features = {
        feature
        for feature in {Feature.TRAILING_COMMA_IN_CALL, Feature.TRAILING_COMMA_IN_DEF}
        if supports_feature(versions, feature)
    }
    for current_line in lines.visit(src_node):
        dst_contents.append(str(empty_line) * after)
        before, after = elt.maybe_empty_lines(current_line)
        dst_contents.append(str(empty_line) * before)
        for line in transform_line(
            current_line, mode=mode, features=split_line_features
        ):
            dst_contents.append(str(line))
    return "".join(dst_contents)


def decode_bytes(src: bytes) -> Tuple[FileContent, Encoding, NewLine]:
    """Return a tuple of (decoded_contents, encoding, newline).

    `newline` is either CRLF or LF but `decoded_contents` is decoded with
    universal newlines (i.e. only contains LF).
    """
    srcbuf = io.BytesIO(src)
    encoding, lines = tokenize.detect_encoding(srcbuf.readline)
    if not lines:
        return "", encoding, "\n"

    newline = "\r\n" if b"\r\n" == lines[0][-2:] else "\n"
    srcbuf.seek(0)
    with io.TextIOWrapper(srcbuf, encoding) as tiow:
        return tiow.read(), encoding, newline


def get_grammars(target_versions: Set[TargetVersion]) -> List[Grammar]:
    if not target_versions:
        # No target_version specified, so try all grammars.
        return [
            # Python 3.7+
            pygram.python_grammar_no_print_statement_no_exec_statement_async_keywords,
            # Python 3.0-3.6
            pygram.python_grammar_no_print_statement_no_exec_statement,
            # Python 2.7 with future print_function import
            pygram.python_grammar_no_print_statement,
            # Python 2.7
            pygram.python_grammar,
        ]

    if all(version.is_python2() for version in target_versions):
        # Python 2-only code, so try Python 2 grammars.
        return [
            # Python 2.7 with future print_function import
            pygram.python_grammar_no_print_statement,
            # Python 2.7
            pygram.python_grammar,
        ]

    # Python 3-compatible code, so only try Python 3 grammar.
    grammars = []
    # If we have to parse both, try to parse async as a keyword first
    if not supports_feature(target_versions, Feature.ASYNC_IDENTIFIERS):
        # Python 3.7+
        grammars.append(
            pygram.python_grammar_no_print_statement_no_exec_statement_async_keywords
        )
    if not supports_feature(target_versions, Feature.ASYNC_KEYWORDS):
        # Python 3.0-3.6
        grammars.append(pygram.python_grammar_no_print_statement_no_exec_statement)
    # At least one of the above branches must have been taken, because every Python
    # version has exactly one of the two 'ASYNC_*' flags
    return grammars


def lib2to3_parse(src_txt: str, target_versions: Iterable[TargetVersion] = ()) -> Node:
    """Given a string with source, return the lib2to3 Node."""
    if not src_txt.endswith("\n"):
        src_txt += "\n"

    for grammar in get_grammars(set(target_versions)):
        drv = driver.Driver(grammar, pytree.convert)
        try:
            result = drv.parse_string(src_txt, True)
            break

        except ParseError as pe:
            lineno, column = pe.context[1]
            lines = src_txt.splitlines()
            try:
                faulty_line = lines[lineno - 1]
            except IndexError:
                faulty_line = "<line number missing in source>"
            exc = InvalidInput(f"Cannot parse: {lineno}:{column}: {faulty_line}")
    else:
        raise exc from None

    if isinstance(result, Leaf):
        result = Node(syms.file_input, [result])
    return result


def lib2to3_unparse(node: Node) -> str:
    """Given a lib2to3 node, return its string representation."""
    code = str(node)
    return code


class Visitor(Generic[T]):
    """Basic lib2to3 visitor that yields things of type `T` on `visit()`."""

    def visit(self, node: LN) -> Iterator[T]:
        """Main method to visit `node` and its children.

        It tries to find a `visit_*()` method for the given `node.type`, like
        `visit_simple_stmt` for Node objects or `visit_INDENT` for Leaf objects.
        If no dedicated `visit_*()` method is found, chooses `visit_default()`
        instead.

        Then yields objects of type `T` from the selected visitor.
        """
        if node.type < 256:
            name = token.tok_name[node.type]
        else:
            name = str(type_repr(node.type))
        # We explicitly branch on whether a visitor exists (instead of
        # using self.visit_default as the default arg to getattr) in order
        # to save needing to create a bound method object and so mypyc can
        # generate a native call to visit_default.
        visitf = getattr(self, f"visit_{name}", None)
        if visitf:
            yield from visitf(node)
        else:
            yield from self.visit_default(node)

    def visit_default(self, node: LN) -> Iterator[T]:
        """Default `visit_*()` implementation. Recurses to children of `node`."""
        if isinstance(node, Node):
            for child in node.children:
                yield from self.visit(child)


@dataclass
class DebugVisitor(Visitor[T]):
    tree_depth: int = 0

    def visit_default(self, node: LN) -> Iterator[T]:
        indent = " " * (2 * self.tree_depth)
        if isinstance(node, Node):
            _type = type_repr(node.type)
            out(f"{indent}{_type}", fg="yellow")
            self.tree_depth += 1
            for child in node.children:
                yield from self.visit(child)

            self.tree_depth -= 1
            out(f"{indent}/{_type}", fg="yellow", bold=False)
        else:
            _type = token.tok_name.get(node.type, str(node.type))
            out(f"{indent}{_type}", fg="blue", nl=False)
            if node.prefix:
                # We don't have to handle prefixes for `Node` objects since
                # that delegates to the first child anyway.
                out(f" {node.prefix!r}", fg="green", bold=False, nl=False)
            out(f" {node.value!r}", fg="blue", bold=False)

    @classmethod
    def show(cls, code: Union[str, Leaf, Node]) -> None:
        """Pretty-print the lib2to3 AST of a given string of `code`.

        Convenience method for debugging.
        """
        v: DebugVisitor[None] = DebugVisitor()
        if isinstance(code, str):
            code = lib2to3_parse(code)
        list(v.visit(code))


WHITESPACE: Final = {token.DEDENT, token.INDENT, token.NEWLINE}
STATEMENT: Final = {
    syms.if_stmt,
    syms.while_stmt,
    syms.for_stmt,
    syms.try_stmt,
    syms.except_clause,
    syms.with_stmt,
    syms.funcdef,
    syms.classdef,
}
STANDALONE_COMMENT: Final = 153
token.tok_name[STANDALONE_COMMENT] = "STANDALONE_COMMENT"
LOGIC_OPERATORS: Final = {"and", "or"}
COMPARATORS: Final = {
    token.LESS,
    token.GREATER,
    token.EQEQUAL,
    token.NOTEQUAL,
    token.LESSEQUAL,
    token.GREATEREQUAL,
}
MATH_OPERATORS: Final = {
    token.VBAR,
    token.CIRCUMFLEX,
    token.AMPER,
    token.LEFTSHIFT,
    token.RIGHTSHIFT,
    token.PLUS,
    token.MINUS,
    token.STAR,
    token.SLASH,
    token.DOUBLESLASH,
    token.PERCENT,
    token.AT,
    token.TILDE,
    token.DOUBLESTAR,
}
STARS: Final = {token.STAR, token.DOUBLESTAR}
VARARGS_SPECIALS: Final = STARS | {token.SLASH}
VARARGS_PARENTS: Final = {
    syms.arglist,
    syms.argument,  # double star in arglist
    syms.trailer,  # single argument to call
    syms.typedargslist,
    syms.varargslist,  # lambdas
}
UNPACKING_PARENTS: Final = {
    syms.atom,  # single element of a list or set literal
    syms.dictsetmaker,
    syms.listmaker,
    syms.testlist_gexp,
    syms.testlist_star_expr,
}
TEST_DESCENDANTS: Final = {
    syms.test,
    syms.lambdef,
    syms.or_test,
    syms.and_test,
    syms.not_test,
    syms.comparison,
    syms.star_expr,
    syms.expr,
    syms.xor_expr,
    syms.and_expr,
    syms.shift_expr,
    syms.arith_expr,
    syms.trailer,
    syms.term,
    syms.power,
}
ASSIGNMENTS: Final = {
    "=",
    "+=",
    "-=",
    "*=",
    "@=",
    "/=",
    "%=",
    "&=",
    "|=",
    "^=",
    "<<=",
    ">>=",
    "**=",
    "//=",
}
COMPREHENSION_PRIORITY: Final = 20
COMMA_PRIORITY: Final = 18
TERNARY_PRIORITY: Final = 16
LOGIC_PRIORITY: Final = 14
STRING_PRIORITY: Final = 12
COMPARATOR_PRIORITY: Final = 10
MATH_PRIORITIES: Final = {
    token.VBAR: 9,
    token.CIRCUMFLEX: 8,
    token.AMPER: 7,
    token.LEFTSHIFT: 6,
    token.RIGHTSHIFT: 6,
    token.PLUS: 5,
    token.MINUS: 5,
    token.STAR: 4,
    token.SLASH: 4,
    token.DOUBLESLASH: 4,
    token.PERCENT: 4,
    token.AT: 4,
    token.TILDE: 3,
    token.DOUBLESTAR: 2,
}
DOT_PRIORITY: Final = 1


@dataclass
class BracketTracker:
    """Keeps track of brackets on a line."""

    depth: int = 0
    bracket_match: Dict[Tuple[Depth, NodeType], Leaf] = field(default_factory=dict)
    delimiters: Dict[LeafID, Priority] = field(default_factory=dict)
    previous: Optional[Leaf] = None
    _for_loop_depths: List[int] = field(default_factory=list)
    _lambda_argument_depths: List[int] = field(default_factory=list)
    invisible: List[Leaf] = field(default_factory=list)

    def mark(self, leaf: Leaf) -> None:
        """Mark `leaf` with bracket-related metadata. Keep track of delimiters.

        All leaves receive an int `bracket_depth` field that stores how deep
        within brackets a given leaf is. 0 means there are no enclosing brackets
        that started on this line.

        If a leaf is itself a closing bracket, it receives an `opening_bracket`
        field that it forms a pair with. This is a one-directional link to
        avoid reference cycles.

        If a leaf is a delimiter (a token on which Black can split the line if
        needed) and it's on depth 0, its `id()` is stored in the tracker's
        `delimiters` field.
        """
        if leaf.type == token.COMMENT:
            return

        self.maybe_decrement_after_for_loop_variable(leaf)
        self.maybe_decrement_after_lambda_arguments(leaf)
        if leaf.type in CLOSING_BRACKETS:
            self.depth -= 1
            try:
                opening_bracket = self.bracket_match.pop((self.depth, leaf.type))
            except KeyError as e:
                raise BracketMatchError(
                    "Unable to match a closing bracket to the following opening"
                    f" bracket: {leaf}"
                ) from e
            leaf.opening_bracket = opening_bracket
            if not leaf.value:
                self.invisible.append(leaf)
        leaf.bracket_depth = self.depth
        if self.depth == 0:
            delim = is_split_before_delimiter(leaf, self.previous)
            if delim and self.previous is not None:
                self.delimiters[id(self.previous)] = delim
            else:
                delim = is_split_after_delimiter(leaf, self.previous)
                if delim:
                    self.delimiters[id(leaf)] = delim
        if leaf.type in OPENING_BRACKETS:
            self.bracket_match[self.depth, BRACKET[leaf.type]] = leaf
            self.depth += 1
            if not leaf.value:
                self.invisible.append(leaf)
        self.previous = leaf
        self.maybe_increment_lambda_arguments(leaf)
        self.maybe_increment_for_loop_variable(leaf)

    def any_open_brackets(self) -> bool:
        """Return True if there is an yet unmatched open bracket on the line."""
        return bool(self.bracket_match)

    def max_delimiter_priority(self, exclude: Iterable[LeafID] = ()) -> Priority:
        """Return the highest priority of a delimiter found on the line.

        Values are consistent with what `is_split_*_delimiter()` return.
        Raises ValueError on no delimiters.
        """
        return max(v for k, v in self.delimiters.items() if k not in exclude)

    def delimiter_count_with_priority(self, priority: Priority = 0) -> int:
        """Return the number of delimiters with the given `priority`.

        If no `priority` is passed, defaults to max priority on the line.
        """
        if not self.delimiters:
            return 0

        priority = priority or self.max_delimiter_priority()
        return sum(1 for p in self.delimiters.values() if p == priority)

    def maybe_increment_for_loop_variable(self, leaf: Leaf) -> bool:
        """In a for loop, or comprehension, the variables are often unpacks.

        To avoid splitting on the comma in this situation, increase the depth of
        tokens between `for` and `in`.
        """
        if leaf.type == token.NAME and leaf.value == "for":
            self.depth += 1
            self._for_loop_depths.append(self.depth)
            return True

        return False

    def maybe_decrement_after_for_loop_variable(self, leaf: Leaf) -> bool:
        """See `maybe_increment_for_loop_variable` above for explanation."""
        if (
            self._for_loop_depths
            and self._for_loop_depths[-1] == self.depth
            and leaf.type == token.NAME
            and leaf.value == "in"
        ):
            self.depth -= 1
            self._for_loop_depths.pop()
            return True

        return False

    def maybe_increment_lambda_arguments(self, leaf: Leaf) -> bool:
        """In a lambda expression, there might be more than one argument.

        To avoid splitting on the comma in this situation, increase the depth of
        tokens between `lambda` and `:`.
        """
        if leaf.type == token.NAME and leaf.value == "lambda":
            self.depth += 1
            self._lambda_argument_depths.append(self.depth)
            return True

        return False

    def maybe_decrement_after_lambda_arguments(self, leaf: Leaf) -> bool:
        """See `maybe_increment_lambda_arguments` above for explanation."""
        if (
            self._lambda_argument_depths
            and self._lambda_argument_depths[-1] == self.depth
            and leaf.type == token.COLON
        ):
            self.depth -= 1
            self._lambda_argument_depths.pop()
            return True

        return False

    def get_open_lsqb(self) -> Optional[Leaf]:
        """Return the most recent opening square bracket (if any)."""
        return self.bracket_match.get((self.depth - 1, token.RSQB))


@dataclass
class Line:
    """Holds leaves and comments. Can be printed with `str(line)`."""

    mode: Mode
    depth: int = 0
    leaves: List[Leaf] = field(default_factory=list)
    # keys ordered like `leaves`
    comments: Dict[LeafID, List[Leaf]] = field(default_factory=dict)
    bracket_tracker: BracketTracker = field(default_factory=BracketTracker)
    inside_brackets: bool = False
    should_split_rhs: bool = False
    magic_trailing_comma: Optional[Leaf] = None

    def append(self, leaf: Leaf, preformatted: bool = False) -> None:
        """Add a new `leaf` to the end of the line.

        Unless `preformatted` is True, the `leaf` will receive a new consistent
        whitespace prefix and metadata applied by :class:`BracketTracker`.
        Trailing commas are maybe removed, unpacked for loop variables are
        demoted from being delimiters.

        Inline comments are put aside.
        """
        has_value = leaf.type in BRACKETS or bool(leaf.value.strip())
        if not has_value:
            return

        if token.COLON == leaf.type and self.is_class_paren_empty:
            del self.leaves[-2:]
        if self.leaves and not preformatted:
            # Note: at this point leaf.prefix should be empty except for
            # imports, for which we only preserve newlines.
            leaf.prefix += whitespace(
                leaf, complex_subscript=self.is_complex_subscript(leaf)
            )
        if self.inside_brackets or not preformatted:
            self.bracket_tracker.mark(leaf)
            if self.mode.magic_trailing_comma:
                if self.has_magic_trailing_comma(leaf):
                    self.magic_trailing_comma = leaf
            elif self.has_magic_trailing_comma(leaf, ensure_removable=True):
                self.remove_trailing_comma()
        if not self.append_comment(leaf):
            self.leaves.append(leaf)

    def append_safe(self, leaf: Leaf, preformatted: bool = False) -> None:
        """Like :func:`append()` but disallow invalid standalone comment structure.

        Raises ValueError when any `leaf` is appended after a standalone comment
        or when a standalone comment is not the first leaf on the line.
        """
        if self.bracket_tracker.depth == 0:
            if self.is_comment:
                raise ValueError("cannot append to standalone comments")

            if self.leaves and leaf.type == STANDALONE_COMMENT:
                raise ValueError(
                    "cannot append standalone comments to a populated line"
                )

        self.append(leaf, preformatted=preformatted)

    @property
    def is_comment(self) -> bool:
        """Is this line a standalone comment?"""
        return len(self.leaves) == 1 and self.leaves[0].type == STANDALONE_COMMENT

    @property
    def is_decorator(self) -> bool:
        """Is this line a decorator?"""
        return bool(self) and self.leaves[0].type == token.AT

    @property
    def is_import(self) -> bool:
        """Is this an import line?"""
        return bool(self) and is_import(self.leaves[0])

    @property
    def is_class(self) -> bool:
        """Is this line a class definition?"""
        return (
            bool(self)
            and self.leaves[0].type == token.NAME
            and self.leaves[0].value == "class"
        )

    @property
    def is_stub_class(self) -> bool:
        """Is this line a class definition with a body consisting only of "..."?"""
        return self.is_class and self.leaves[-3:] == [
            Leaf(token.DOT, ".") for _ in range(3)
        ]

    @property
    def is_def(self) -> bool:
        """Is this a function definition? (Also returns True for async defs.)"""
        try:
            first_leaf = self.leaves[0]
        except IndexError:
            return False

        try:
            second_leaf: Optional[Leaf] = self.leaves[1]
        except IndexError:
            second_leaf = None
        return (first_leaf.type == token.NAME and first_leaf.value == "def") or (
            first_leaf.type == token.ASYNC
            and second_leaf is not None
            and second_leaf.type == token.NAME
            and second_leaf.value == "def"
        )

    @property
    def is_class_paren_empty(self) -> bool:
        """Is this a class with no base classes but using parentheses?

        Those are unnecessary and should be removed.
        """
        return (
            bool(self)
            and len(self.leaves) == 4
            and self.is_class
            and self.leaves[2].type == token.LPAR
            and self.leaves[2].value == "("
            and self.leaves[3].type == token.RPAR
            and self.leaves[3].value == ")"
        )

    @property
    def is_triple_quoted_string(self) -> bool:
        """Is the line a triple quoted string?"""
        return (
            bool(self)
            and self.leaves[0].type == token.STRING
            and self.leaves[0].value.startswith(('"""', "'''"))
        )

    def contains_standalone_comments(self, depth_limit: int = sys.maxsize) -> bool:
        """If so, needs to be split before emitting."""
        for leaf in self.leaves:
            if leaf.type == STANDALONE_COMMENT and leaf.bracket_depth <= depth_limit:
                return True

        return False

    def contains_uncollapsable_type_comments(self) -> bool:
        ignored_ids = set()
        try:
            last_leaf = self.leaves[-1]
            ignored_ids.add(id(last_leaf))
            if last_leaf.type == token.COMMA or (
                last_leaf.type == token.RPAR and not last_leaf.value
            ):
                # When trailing commas or optional parens are inserted by Black for
                # consistency, comments after the previous last element are not moved
                # (they don't have to, rendering will still be correct).  So we ignore
                # trailing commas and invisible.
                last_leaf = self.leaves[-2]
                ignored_ids.add(id(last_leaf))
        except IndexError:
            return False

        # A type comment is uncollapsable if it is attached to a leaf
        # that isn't at the end of the line (since that could cause it
        # to get associated to a different argument) or if there are
        # comments before it (since that could cause it to get hidden
        # behind a comment.
        comment_seen = False
        for leaf_id, comments in self.comments.items():
            for comment in comments:
                if is_type_comment(comment):
                    if comment_seen or (
                        not is_type_comment(comment, " ignore")
                        and leaf_id not in ignored_ids
                    ):
                        return True

                comment_seen = True

        return False

    def contains_unsplittable_type_ignore(self) -> bool:
        if not self.leaves:
            return False

        # If a 'type: ignore' is attached to the end of a line, we
        # can't split the line, because we can't know which of the
        # subexpressions the ignore was meant to apply to.
        #
        # We only want this to apply to actual physical lines from the
        # original source, though: we don't want the presence of a
        # 'type: ignore' at the end of a multiline expression to
        # justify pushing it all onto one line. Thus we
        # (unfortunately) need to check the actual source lines and
        # only report an unsplittable 'type: ignore' if this line was
        # one line in the original code.

        # Grab the first and last line numbers, skipping generated leaves
        first_line = next((leaf.lineno for leaf in self.leaves if leaf.lineno != 0), 0)
        last_line = next(
            (leaf.lineno for leaf in reversed(self.leaves) if leaf.lineno != 0), 0
        )

        if first_line == last_line:
            # We look at the last two leaves since a comma or an
            # invisible paren could have been added at the end of the
            # line.
            for node in self.leaves[-2:]:
                for comment in self.comments.get(id(node), []):
                    if is_type_comment(comment, " ignore"):
                        return True

        return False

    def contains_multiline_strings(self) -> bool:
        return any(is_multiline_string(leaf) for leaf in self.leaves)

    def has_magic_trailing_comma(
        self, closing: Leaf, ensure_removable: bool = False
    ) -> bool:
        """Return True if we have a magic trailing comma, that is when:
        - there's a trailing comma here
        - it's not a one-tuple
        Additionally, if ensure_removable:
        - it's not from square bracket indexing
        """
        if not (
            closing.type in CLOSING_BRACKETS
            and self.leaves
            and self.leaves[-1].type == token.COMMA
        ):
            return False

        if closing.type == token.RBRACE:
            return True

        if closing.type == token.RSQB:
            if not ensure_removable:
                return True
            comma = self.leaves[-1]
            return bool(comma.parent and comma.parent.type == syms.listmaker)

        if self.is_import:
            return True

        if not is_one_tuple_between(closing.opening_bracket, closing, self.leaves):
            return True

        return False

    def append_comment(self, comment: Leaf) -> bool:
        """Add an inline or standalone comment to the line."""
        if (
            comment.type == STANDALONE_COMMENT
            and self.bracket_tracker.any_open_brackets()
        ):
            comment.prefix = ""
            return False

        if comment.type != token.COMMENT:
            return False

        if not self.leaves:
            comment.type = STANDALONE_COMMENT
            comment.prefix = ""
            return False

        last_leaf = self.leaves[-1]
        if (
            last_leaf.type == token.RPAR
            and not last_leaf.value
            and last_leaf.parent
            and len(list(last_leaf.parent.leaves())) <= 3
            and not is_type_comment(comment)
        ):
            # Comments on an optional parens wrapping a single leaf should belong to
            # the wrapped node except if it's a type comment. Pinning the comment like
            # this avoids unstable formatting caused by comment migration.
            if len(self.leaves) < 2:
                comment.type = STANDALONE_COMMENT
                comment.prefix = ""
                return False

            last_leaf = self.leaves[-2]
        self.comments.setdefault(id(last_leaf), []).append(comment)
        return True

    def comments_after(self, leaf: Leaf) -> List[Leaf]:
        """Generate comments that should appear directly after `leaf`."""
        return self.comments.get(id(leaf), [])

    def remove_trailing_comma(self) -> None:
        """Remove the trailing comma and moves the comments attached to it."""
        trailing_comma = self.leaves.pop()
        trailing_comma_comments = self.comments.pop(id(trailing_comma), [])
        self.comments.setdefault(id(self.leaves[-1]), []).extend(
            trailing_comma_comments
        )

    def is_complex_subscript(self, leaf: Leaf) -> bool:
        """Return True iff `leaf` is part of a slice with non-trivial exprs."""
        open_lsqb = self.bracket_tracker.get_open_lsqb()
        if open_lsqb is None:
            return False

        subscript_start = open_lsqb.next_sibling

        if isinstance(subscript_start, Node):
            if subscript_start.type == syms.listmaker:
                return False

            if subscript_start.type == syms.subscriptlist:
                subscript_start = child_towards(subscript_start, leaf)
        return subscript_start is not None and any(
            n.type in TEST_DESCENDANTS for n in subscript_start.pre_order()
        )

    def clone(self) -> "Line":
        return Line(
            mode=self.mode,
            depth=self.depth,
            inside_brackets=self.inside_brackets,
            should_split_rhs=self.should_split_rhs,
            magic_trailing_comma=self.magic_trailing_comma,
        )

    def __str__(self) -> str:
        """Render the line."""
        if not self:
            return "\n"

        indent = "    " * self.depth
        leaves = iter(self.leaves)
        first = next(leaves)
        res = f"{first.prefix}{indent}{first.value}"
        for leaf in leaves:
            res += str(leaf)
        for comment in itertools.chain.from_iterable(self.comments.values()):
            res += str(comment)

        return res + "\n"

    def __bool__(self) -> bool:
        """Return True if the line has leaves or comments."""
        return bool(self.leaves or self.comments)


@dataclass
class EmptyLineTracker:
    """Provides a stateful method that returns the number of potential extra
    empty lines needed before and after the currently processed line.

    Note: this tracker works on lines that haven't been split yet.  It assumes
    the prefix of the first leaf consists of optional newlines.  Those newlines
    are consumed by `maybe_empty_lines()` and included in the computation.
    """

    is_pyi: bool = False
    previous_line: Optional[Line] = None
    previous_after: int = 0
    previous_defs: List[int] = field(default_factory=list)

    def maybe_empty_lines(self, current_line: Line) -> Tuple[int, int]:
        """Return the number of extra empty lines before and after the `current_line`.

        This is for separating `def`, `async def` and `class` with extra empty
        lines (two on module-level).
        """
        before, after = self._maybe_empty_lines(current_line)
        before = (
            # Black should not insert empty lines at the beginning
            # of the file
            0
            if self.previous_line is None
            else before - self.previous_after
        )
        self.previous_after = after
        self.previous_line = current_line
        return before, after

    def _maybe_empty_lines(self, current_line: Line) -> Tuple[int, int]:
        max_allowed = 1
        if current_line.depth == 0:
            max_allowed = 1 if self.is_pyi else 2
        if current_line.leaves:
            # Consume the first leaf's extra newlines.
            first_leaf = current_line.leaves[0]
            before = first_leaf.prefix.count("\n")
            before = min(before, max_allowed)
            first_leaf.prefix = ""
        else:
            before = 0
        depth = current_line.depth
        while self.previous_defs and self.previous_defs[-1] >= depth:
            self.previous_defs.pop()
            if self.is_pyi:
                before = 0 if depth else 1
            else:
                before = 1 if depth else 2
        if current_line.is_decorator or current_line.is_def or current_line.is_class:
            return self._maybe_empty_lines_for_class_or_def(current_line, before)

        if (
            self.previous_line
            and self.previous_line.is_import
            and not current_line.is_import
            and depth == self.previous_line.depth
        ):
            return (before or 1), 0

        if (
            self.previous_line
            and self.previous_line.is_class
            and current_line.is_triple_quoted_string
        ):
            return before, 1

        return before, 0

    def _maybe_empty_lines_for_class_or_def(
        self, current_line: Line, before: int
    ) -> Tuple[int, int]:
        if not current_line.is_decorator:
            self.previous_defs.append(current_line.depth)
        if self.previous_line is None:
            # Don't insert empty lines before the first line in the file.
            return 0, 0

        if self.previous_line.is_decorator:
            if self.is_pyi and current_line.is_stub_class:
                # Insert an empty line after a decorated stub class
                return 0, 1

            return 0, 0

        if self.previous_line.depth < current_line.depth and (
            self.previous_line.is_class or self.previous_line.is_def
        ):
            return 0, 0

        if (
            self.previous_line.is_comment
            and self.previous_line.depth == current_line.depth
            and before == 0
        ):
            return 0, 0

        if self.is_pyi:
            if self.previous_line.depth > current_line.depth:
                newlines = 1
            elif current_line.is_class or self.previous_line.is_class:
                if current_line.is_stub_class and self.previous_line.is_stub_class:
                    # No blank line between classes with an empty body
                    newlines = 0
                else:
                    newlines = 1
            elif (
                current_line.is_def or current_line.is_decorator
            ) and not self.previous_line.is_def:
                # Blank line between a block of functions (maybe with preceding
                # decorators) and a block of non-functions
                newlines = 1
            else:
                newlines = 0
        else:
            newlines = 2
        if current_line.depth and newlines:
            newlines -= 1
        return newlines, 0


@dataclass
class LineGenerator(Visitor[Line]):
    """Generates reformatted Line objects.  Empty lines are not emitted.

    Note: destroys the tree it's visiting by mutating prefixes of its leaves
    in ways that will no longer stringify to valid Python code on the tree.
    """

    mode: Mode
    remove_u_prefix: bool = False
    current_line: Line = field(init=False)

    def line(self, indent: int = 0) -> Iterator[Line]:
        """Generate a line.

        If the line is empty, only emit if it makes sense.
        If the line is too long, split it first and then generate.

        If any lines were generated, set up a new current_line.
        """
        if not self.current_line:
            self.current_line.depth += indent
            return  # Line is empty, don't emit. Creating a new one unnecessary.

        complete_line = self.current_line
        self.current_line = Line(mode=self.mode, depth=complete_line.depth + indent)
        yield complete_line

    def visit_default(self, node: LN) -> Iterator[Line]:
        """Default `visit_*()` implementation. Recurses to children of `node`."""
        if isinstance(node, Leaf):
            any_open_brackets = self.current_line.bracket_tracker.any_open_brackets()
            for comment in generate_comments(node):
                if any_open_brackets:
                    # any comment within brackets is subject to splitting
                    self.current_line.append(comment)
                elif comment.type == token.COMMENT:
                    # regular trailing comment
                    self.current_line.append(comment)
                    yield from self.line()

                else:
                    # regular standalone comment
                    yield from self.line()

                    self.current_line.append(comment)
                    yield from self.line()

            normalize_prefix(node, inside_brackets=any_open_brackets)
            if self.mode.string_normalization and node.type == token.STRING:
                normalize_string_prefix(node, remove_u_prefix=self.remove_u_prefix)
                normalize_string_quotes(node)
            if node.type == token.NUMBER:
                normalize_numeric_literal(node)
            if node.type not in WHITESPACE:
                self.current_line.append(node)
        yield from super().visit_default(node)

    def visit_INDENT(self, node: Leaf) -> Iterator[Line]:
        """Increase indentation level, maybe yield a line."""
        # In blib2to3 INDENT never holds comments.
        yield from self.line(+1)
        yield from self.visit_default(node)

    def visit_DEDENT(self, node: Leaf) -> Iterator[Line]:
        """Decrease indentation level, maybe yield a line."""
        # The current line might still wait for trailing comments.  At DEDENT time
        # there won't be any (they would be prefixes on the preceding NEWLINE).
        # Emit the line then.
        yield from self.line()

        # While DEDENT has no value, its prefix may contain standalone comments
        # that belong to the current indentation level.  Get 'em.
        yield from self.visit_default(node)

        # Finally, emit the dedent.
        yield from self.line(-1)

    def visit_stmt(
        self, node: Node, keywords: Set[str], parens: Set[str]
    ) -> Iterator[Line]:
        """Visit a statement.

        This implementation is shared for `if`, `while`, `for`, `try`, `except`,
        `def`, `with`, `class`, `assert` and assignments.

        The relevant Python language `keywords` for a given statement will be
        NAME leaves within it. This methods puts those on a separate line.

        `parens` holds a set of string leaf values immediately after which
        invisible parens should be put.
        """
        normalize_invisible_parens(node, parens_after=parens)
        for child in node.children:
            if child.type == token.NAME and child.value in keywords:  # type: ignore
                yield from self.line()

            yield from self.visit(child)

    def visit_suite(self, node: Node) -> Iterator[Line]:
        """Visit a suite."""
        if self.mode.is_pyi and is_stub_suite(node):
            yield from self.visit(node.children[2])
        else:
            yield from self.visit_default(node)

    def visit_simple_stmt(self, node: Node) -> Iterator[Line]:
        """Visit a statement without nested statements."""
        if first_child_is_arith(node):
            wrap_in_parentheses(node, node.children[0], visible=False)
        is_suite_like = node.parent and node.parent.type in STATEMENT
        if is_suite_like:
            if self.mode.is_pyi and is_stub_body(node):
                yield from self.visit_default(node)
            else:
                yield from self.line(+1)
                yield from self.visit_default(node)
                yield from self.line(-1)

        else:
            if (
                not self.mode.is_pyi
                or not node.parent
                or not is_stub_suite(node.parent)
            ):
                yield from self.line()
            yield from self.visit_default(node)

    def visit_async_stmt(self, node: Node) -> Iterator[Line]:
        """Visit `async def`, `async for`, `async with`."""
        yield from self.line()

        children = iter(node.children)
        for child in children:
            yield from self.visit(child)

            if child.type == token.ASYNC:
                break

        internal_stmt = next(children)
        for child in internal_stmt.children:
            yield from self.visit(child)

    def visit_decorators(self, node: Node) -> Iterator[Line]:
        """Visit decorators."""
        for child in node.children:
            yield from self.line()
            yield from self.visit(child)

    def visit_SEMI(self, leaf: Leaf) -> Iterator[Line]:
        """Remove a semicolon and put the other statement on a separate line."""
        yield from self.line()

    def visit_ENDMARKER(self, leaf: Leaf) -> Iterator[Line]:
        """End of file. Process outstanding comments and end with a newline."""
        yield from self.visit_default(leaf)
        yield from self.line()

    def visit_STANDALONE_COMMENT(self, leaf: Leaf) -> Iterator[Line]:
        if not self.current_line.bracket_tracker.any_open_brackets():
            yield from self.line()
        yield from self.visit_default(leaf)

    def visit_factor(self, node: Node) -> Iterator[Line]:
        """Force parentheses between a unary op and a binary power:

        -2 ** 8 -> -(2 ** 8)
        """
        _operator, operand = node.children
        if (
            operand.type == syms.power
            and len(operand.children) == 3
            and operand.children[1].type == token.DOUBLESTAR
        ):
            lpar = Leaf(token.LPAR, "(")
            rpar = Leaf(token.RPAR, ")")
            index = operand.remove() or 0
            node.insert_child(index, Node(syms.atom, [lpar, operand, rpar]))
        yield from self.visit_default(node)

    def visit_STRING(self, leaf: Leaf) -> Iterator[Line]:
        if is_docstring(leaf) and "\\\n" not in leaf.value:
            # We're ignoring docstrings with backslash newline escapes because changing
            # indentation of those changes the AST representation of the code.
            prefix = get_string_prefix(leaf.value)
            docstring = leaf.value[len(prefix) :]  # Remove the prefix
            quote_char = docstring[0]
            # A natural way to remove the outer quotes is to do:
            #   docstring = docstring.strip(quote_char)
            # but that breaks on """""x""" (which is '""x').
            # So we actually need to remove the first character and the next two
            # characters but only if they are the same as the first.
            quote_len = 1 if docstring[1] != quote_char else 3
            docstring = docstring[quote_len:-quote_len]

            if is_multiline_string(leaf):
                indent = " " * 4 * self.current_line.depth
                docstring = fix_docstring(docstring, indent)
            else:
                docstring = docstring.strip()

            if docstring:
                # Add some padding if the docstring starts / ends with a quote mark.
                if docstring[0] == quote_char:
                    docstring = " " + docstring
                if docstring[-1] == quote_char:
                    docstring += " "
                if docstring[-1] == "\\":
                    backslash_count = len(docstring) - len(docstring.rstrip("\\"))
                    if backslash_count % 2:
                        # Odd number of tailing backslashes, add some padding to
                        # avoid escaping the closing string quote.
                        docstring += " "
            else:
                # Add some padding if the docstring is empty.
                docstring = " "

            # We could enforce triple quotes at this point.
            quote = quote_char * quote_len
            leaf.value = prefix + quote + docstring + quote

        yield from self.visit_default(leaf)

    def __post_init__(self) -> None:
        """You are in a twisty little maze of passages."""
        self.current_line = Line(mode=self.mode)

        v = self.visit_stmt
        Ø: Set[str] = set()
        self.visit_assert_stmt = partial(v, keywords={"assert"}, parens={"assert", ","})
        self.visit_if_stmt = partial(
            v, keywords={"if", "else", "elif"}, parens={"if", "elif"}
        )
        self.visit_while_stmt = partial(v, keywords={"while", "else"}, parens={"while"})
        self.visit_for_stmt = partial(v, keywords={"for", "else"}, parens={"for", "in"})
        self.visit_try_stmt = partial(
            v, keywords={"try", "except", "else", "finally"}, parens=Ø
        )
        self.visit_except_clause = partial(v, keywords={"except"}, parens=Ø)
        self.visit_with_stmt = partial(v, keywords={"with"}, parens=Ø)
        self.visit_funcdef = partial(v, keywords={"def"}, parens=Ø)
        self.visit_classdef = partial(v, keywords={"class"}, parens=Ø)
        self.visit_expr_stmt = partial(v, keywords=Ø, parens=ASSIGNMENTS)
        self.visit_return_stmt = partial(v, keywords={"return"}, parens={"return"})
        self.visit_import_from = partial(v, keywords=Ø, parens={"import"})
        self.visit_del_stmt = partial(v, keywords=Ø, parens={"del"})
        self.visit_async_funcdef = self.visit_async_stmt
        self.visit_decorated = self.visit_decorators


IMPLICIT_TUPLE = {syms.testlist, syms.testlist_star_expr, syms.exprlist}
BRACKET = {token.LPAR: token.RPAR, token.LSQB: token.RSQB, token.LBRACE: token.RBRACE}
OPENING_BRACKETS = set(BRACKET.keys())
CLOSING_BRACKETS = set(BRACKET.values())
BRACKETS = OPENING_BRACKETS | CLOSING_BRACKETS
ALWAYS_NO_SPACE = CLOSING_BRACKETS | {token.COMMA, STANDALONE_COMMENT}


def whitespace(leaf: Leaf, *, complex_subscript: bool) -> str:  # noqa: C901
    """Return whitespace prefix if needed for the given `leaf`.

    `complex_subscript` signals whether the given leaf is part of a subscription
    which has non-trivial arguments, like arithmetic expressions or function calls.
    """
    NO = ""
    SPACE = " "
    DOUBLESPACE = "  "
    t = leaf.type
    p = leaf.parent
    v = leaf.value
    if t in ALWAYS_NO_SPACE:
        return NO

    if t == token.COMMENT:
        return DOUBLESPACE

    assert p is not None, f"INTERNAL ERROR: hand-made leaf without parent: {leaf!r}"
    if t == token.COLON and p.type not in {
        syms.subscript,
        syms.subscriptlist,
        syms.sliceop,
    }:
        return NO

    prev = leaf.prev_sibling
    if not prev:
        prevp = preceding_leaf(p)
        if not prevp or prevp.type in OPENING_BRACKETS:
            return NO

        if t == token.COLON:
            if prevp.type == token.COLON:
                return NO

            elif prevp.type != token.COMMA and not complex_subscript:
                return NO

            return SPACE

        if prevp.type == token.EQUAL:
            if prevp.parent:
                if prevp.parent.type in {
                    syms.arglist,
                    syms.argument,
                    syms.parameters,
                    syms.varargslist,
                }:
                    return NO

                elif prevp.parent.type == syms.typedargslist:
                    # A bit hacky: if the equal sign has whitespace, it means we
                    # previously found it's a typed argument.  So, we're using
                    # that, too.
                    return prevp.prefix

        elif prevp.type in VARARGS_SPECIALS:
            if is_vararg(prevp, within=VARARGS_PARENTS | UNPACKING_PARENTS):
                return NO

        elif prevp.type == token.COLON:
            if prevp.parent and prevp.parent.type in {syms.subscript, syms.sliceop}:
                return SPACE if complex_subscript else NO

        elif (
            prevp.parent
            and prevp.parent.type == syms.factor
            and prevp.type in MATH_OPERATORS
        ):
            return NO

        elif (
            prevp.type == token.RIGHTSHIFT
            and prevp.parent
            and prevp.parent.type == syms.shift_expr
            and prevp.prev_sibling
            and prevp.prev_sibling.type == token.NAME
            and prevp.prev_sibling.value == "print"  # type: ignore
        ):
            # Python 2 print chevron
            return NO
        elif prevp.type == token.AT and p.parent and p.parent.type == syms.decorator:
            # no space in decorators
            return NO

    elif prev.type in OPENING_BRACKETS:
        return NO

    if p.type in {syms.parameters, syms.arglist}:
        # untyped function signatures or calls
        if not prev or prev.type != token.COMMA:
            return NO

    elif p.type == syms.varargslist:
        # lambdas
        if prev and prev.type != token.COMMA:
            return NO

    elif p.type == syms.typedargslist:
        # typed function signatures
        if not prev:
            return NO

        if t == token.EQUAL:
            if prev.type != syms.tname:
                return NO

        elif prev.type == token.EQUAL:
            # A bit hacky: if the equal sign has whitespace, it means we
            # previously found it's a typed argument.  So, we're using that, too.
            return prev.prefix

        elif prev.type != token.COMMA:
            return NO

    elif p.type == syms.tname:
        # type names
        if not prev:
            prevp = preceding_leaf(p)
            if not prevp or prevp.type != token.COMMA:
                return NO

    elif p.type == syms.trailer:
        # attributes and calls
        if t == token.LPAR or t == token.RPAR:
            return NO

        if not prev:
            if t == token.DOT:
                prevp = preceding_leaf(p)
                if not prevp or prevp.type != token.NUMBER:
                    return NO

            elif t == token.LSQB:
                return NO

        elif prev.type != token.COMMA:
            return NO

    elif p.type == syms.argument:
        # single argument
        if t == token.EQUAL:
            return NO

        if not prev:
            prevp = preceding_leaf(p)
            if not prevp or prevp.type == token.LPAR:
                return NO

        elif prev.type in {token.EQUAL} | VARARGS_SPECIALS:
            return NO

    elif p.type == syms.decorator:
        # decorators
        return NO

    elif p.type == syms.dotted_name:
        if prev:
            return NO

        prevp = preceding_leaf(p)
        if not prevp or prevp.type == token.AT or prevp.type == token.DOT:
            return NO

    elif p.type == syms.classdef:
        if t == token.LPAR:
            return NO

        if prev and prev.type == token.LPAR:
            return NO

    elif p.type in {syms.subscript, syms.sliceop}:
        # indexing
        if not prev:
            assert p.parent is not None, "subscripts are always parented"
            if p.parent.type == syms.subscriptlist:
                return SPACE

            return NO

        elif not complex_subscript:
            return NO

    elif p.type == syms.atom:
        if prev and t == token.DOT:
            # dots, but not the first one.
            return NO

    elif p.type == syms.dictsetmaker:
        # dict unpacking
        if prev and prev.type == token.DOUBLESTAR:
            return NO

    elif p.type in {syms.factor, syms.star_expr}:
        # unary ops
        if not prev:
            prevp = preceding_leaf(p)
            if not prevp or prevp.type in OPENING_BRACKETS:
                return NO

            prevp_parent = prevp.parent
            assert prevp_parent is not None
            if prevp.type == token.COLON and prevp_parent.type in {
                syms.subscript,
                syms.sliceop,
            }:
                return NO

            elif prevp.type == token.EQUAL and prevp_parent.type == syms.argument:
                return NO

        elif t in {token.NAME, token.NUMBER, token.STRING}:
            return NO

    elif p.type == syms.import_from:
        if t == token.DOT:
            if prev and prev.type == token.DOT:
                return NO

        elif t == token.NAME:
            if v == "import":
                return SPACE

            if prev and prev.type == token.DOT:
                return NO

    elif p.type == syms.sliceop:
        return NO

    return SPACE


def preceding_leaf(node: Optional[LN]) -> Optional[Leaf]:
    """Return the first leaf that precedes `node`, if any."""
    while node:
        res = node.prev_sibling
        if res:
            if isinstance(res, Leaf):
                return res

            try:
                return list(res.leaves())[-1]

            except IndexError:
                return None

        node = node.parent
    return None


def prev_siblings_are(node: Optional[LN], tokens: List[Optional[NodeType]]) -> bool:
    """Return if the `node` and its previous siblings match types against the provided
    list of tokens; the provided `node`has its type matched against the last element in
    the list.  `None` can be used as the first element to declare that the start of the
    list is anchored at the start of its parent's children."""
    if not tokens:
        return True
    if tokens[-1] is None:
        return node is None
    if not node:
        return False
    if node.type != tokens[-1]:
        return False
    return prev_siblings_are(node.prev_sibling, tokens[:-1])


def child_towards(ancestor: Node, descendant: LN) -> Optional[LN]:
    """Return the child of `ancestor` that contains `descendant`."""
    node: Optional[LN] = descendant
    while node and node.parent != ancestor:
        node = node.parent
    return node


def container_of(leaf: Leaf) -> LN:
    """Return `leaf` or one of its ancestors that is the topmost container of it.

    By "container" we mean a node where `leaf` is the very first child.
    """
    same_prefix = leaf.prefix
    container: LN = leaf
    while container:
        parent = container.parent
        if parent is None:
            break

        if parent.children[0].prefix != same_prefix:
            break

        if parent.type == syms.file_input:
            break

        if parent.prev_sibling is not None and parent.prev_sibling.type in BRACKETS:
            break

        container = parent
    return container


def is_split_after_delimiter(leaf: Leaf, previous: Optional[Leaf] = None) -> Priority:
    """Return the priority of the `leaf` delimiter, given a line break after it.

    The delimiter priorities returned here are from those delimiters that would
    cause a line break after themselves.

    Higher numbers are higher priority.
    """
    if leaf.type == token.COMMA:
        return COMMA_PRIORITY

    return 0


def is_split_before_delimiter(leaf: Leaf, previous: Optional[Leaf] = None) -> Priority:
    """Return the priority of the `leaf` delimiter, given a line break before it.

    The delimiter priorities returned here are from those delimiters that would
    cause a line break before themselves.

    Higher numbers are higher priority.
    """
    if is_vararg(leaf, within=VARARGS_PARENTS | UNPACKING_PARENTS):
        # * and ** might also be MATH_OPERATORS but in this case they are not.
        # Don't treat them as a delimiter.
        return 0

    if (
        leaf.type == token.DOT
        and leaf.parent
        and leaf.parent.type not in {syms.import_from, syms.dotted_name}
        and (previous is None or previous.type in CLOSING_BRACKETS)
    ):
        return DOT_PRIORITY

    if (
        leaf.type in MATH_OPERATORS
        and leaf.parent
        and leaf.parent.type not in {syms.factor, syms.star_expr}
    ):
        return MATH_PRIORITIES[leaf.type]

    if leaf.type in COMPARATORS:
        return COMPARATOR_PRIORITY

    if (
        leaf.type == token.STRING
        and previous is not None
        and previous.type == token.STRING
    ):
        return STRING_PRIORITY

    if leaf.type not in {token.NAME, token.ASYNC}:
        return 0

    if (
        leaf.value == "for"
        and leaf.parent
        and leaf.parent.type in {syms.comp_for, syms.old_comp_for}
        or leaf.type == token.ASYNC
    ):
        if (
            not isinstance(leaf.prev_sibling, Leaf)
            or leaf.prev_sibling.value != "async"
        ):
            return COMPREHENSION_PRIORITY

    if (
        leaf.value == "if"
        and leaf.parent
        and leaf.parent.type in {syms.comp_if, syms.old_comp_if}
    ):
        return COMPREHENSION_PRIORITY

    if leaf.value in {"if", "else"} and leaf.parent and leaf.parent.type == syms.test:
        return TERNARY_PRIORITY

    if leaf.value == "is":
        return COMPARATOR_PRIORITY

    if (
        leaf.value == "in"
        and leaf.parent
        and leaf.parent.type in {syms.comp_op, syms.comparison}
        and not (
            previous is not None
            and previous.type == token.NAME
            and previous.value == "not"
        )
    ):
        return COMPARATOR_PRIORITY

    if (
        leaf.value == "not"
        and leaf.parent
        and leaf.parent.type == syms.comp_op
        and not (
            previous is not None
            and previous.type == token.NAME
            and previous.value == "is"
        )
    ):
        return COMPARATOR_PRIORITY

    if leaf.value in LOGIC_OPERATORS and leaf.parent:
        return LOGIC_PRIORITY

    return 0


FMT_OFF = {"# fmt: off", "# fmt:off", "# yapf: disable"}
FMT_SKIP = {"# fmt: skip", "# fmt:skip"}
FMT_PASS = {*FMT_OFF, *FMT_SKIP}
FMT_ON = {"# fmt: on", "# fmt:on", "# yapf: enable"}


def generate_comments(leaf: LN) -> Iterator[Leaf]:
    """Clean the prefix of the `leaf` and generate comments from it, if any.

    Comments in lib2to3 are shoved into the whitespace prefix.  This happens
    in `pgen2/driver.py:Driver.parse_tokens()`.  This was a brilliant implementation
    move because it does away with modifying the grammar to include all the
    possible places in which comments can be placed.

    The sad consequence for us though is that comments don't "belong" anywhere.
    This is why this function generates simple parentless Leaf objects for
    comments.  We simply don't know what the correct parent should be.

    No matter though, we can live without this.  We really only need to
    differentiate between inline and standalone comments.  The latter don't
    share the line with any code.

    Inline comments are emitted as regular token.COMMENT leaves.  Standalone
    are emitted with a fake STANDALONE_COMMENT token identifier.
    """
    for pc in list_comments(leaf.prefix, is_endmarker=leaf.type == token.ENDMARKER):
        yield Leaf(pc.type, pc.value, prefix="\n" * pc.newlines)


@dataclass
class ProtoComment:
    """Describes a piece of syntax that is a comment.

    It's not a :class:`blib2to3.pytree.Leaf` so that:

    * it can be cached (`Leaf` objects should not be reused more than once as
      they store their lineno, column, prefix, and parent information);
    * `newlines` and `consumed` fields are kept separate from the `value`. This
      simplifies handling of special marker comments like ``# fmt: off/on``.
    """

    type: int  # token.COMMENT or STANDALONE_COMMENT
    value: str  # content of the comment
    newlines: int  # how many newlines before the comment
    consumed: int  # how many characters of the original leaf's prefix did we consume


@lru_cache(maxsize=4096)
def list_comments(prefix: str, *, is_endmarker: bool) -> List[ProtoComment]:
    """Return a list of :class:`ProtoComment` objects parsed from the given `prefix`."""
    result: List[ProtoComment] = []
    if not prefix or "#" not in prefix:
        return result

    consumed = 0
    nlines = 0
    ignored_lines = 0
    for index, line in enumerate(re.split("\r?\n", prefix)):
        consumed += len(line) + 1  # adding the length of the split '\n'
        line = line.lstrip()
        if not line:
            nlines += 1
        if not line.startswith("#"):
            # Escaped newlines outside of a comment are not really newlines at
            # all. We treat a single-line comment following an escaped newline
            # as a simple trailing comment.
            if line.endswith("\\"):
                ignored_lines += 1
            continue

        if index == ignored_lines and not is_endmarker:
            comment_type = token.COMMENT  # simple trailing comment
        else:
            comment_type = STANDALONE_COMMENT
        comment = make_comment(line)
        result.append(
            ProtoComment(
                type=comment_type, value=comment, newlines=nlines, consumed=consumed
            )
        )
        nlines = 0
    return result


def make_comment(content: str) -> str:
    """Return a consistently formatted comment from the given `content` string.

    All comments (except for "##", "#!", "#:", '#'", "#%%") should have a single
    space between the hash sign and the content.

    If `content` didn't start with a hash sign, one is provided.
    """
    content = content.rstrip()
    if not content:
        return "#"

    if content[0] == "#":
        content = content[1:]
    NON_BREAKING_SPACE = " "
    if (
        content
        and content[0] == NON_BREAKING_SPACE
        and not content.lstrip().startswith("type:")
    ):
        content = " " + content[1:]  # Replace NBSP by a simple space
    if content and content[0] not in " !:#'%":
        content = " " + content
    return "#" + content


def transform_line(
    line: Line, mode: Mode, features: Collection[Feature] = ()
) -> Iterator[Line]:
    """Transform a `line`, potentially splitting it into many lines.

    They should fit in the allotted `line_length` but might not be able to.

    `features` are syntactical features that may be used in the output.
    """
    if line.is_comment:
        yield line
        return

    line_str = line_to_string(line)

    def init_st(ST: Type[StringTransformer]) -> StringTransformer:
        """Initialize StringTransformer"""
        return ST(mode.line_length, mode.string_normalization)

    string_merge = init_st(StringMerger)
    string_paren_strip = init_st(StringParenStripper)
    string_split = init_st(StringSplitter)
    string_paren_wrap = init_st(StringParenWrapper)

    transformers: List[Transformer]
    if (
        not line.contains_uncollapsable_type_comments()
        and not line.should_split_rhs
        and not line.magic_trailing_comma
        and (
            is_line_short_enough(line, line_length=mode.line_length, line_str=line_str)
            or line.contains_unsplittable_type_ignore()
        )
        and not (line.inside_brackets and line.contains_standalone_comments())
    ):
        # Only apply basic string preprocessing, since lines shouldn't be split here.
        if mode.experimental_string_processing:
            transformers = [string_merge, string_paren_strip]
        else:
            transformers = []
    elif line.is_def:
        transformers = [left_hand_split]
    else:

        def rhs(line: Line, features: Collection[Feature]) -> Iterator[Line]:
            """Wraps calls to `right_hand_split`.

            The calls increasingly `omit` right-hand trailers (bracket pairs with
            content), meaning the trailers get glued together to split on another
            bracket pair instead.
            """
            for omit in generate_trailers_to_omit(line, mode.line_length):
                lines = list(
                    right_hand_split(line, mode.line_length, features, omit=omit)
                )
                # Note: this check is only able to figure out if the first line of the
                # *current* transformation fits in the line length.  This is true only
                # for simple cases.  All others require running more transforms via
                # `transform_line()`.  This check doesn't know if those would succeed.
                if is_line_short_enough(lines[0], line_length=mode.line_length):
                    yield from lines
                    return

            # All splits failed, best effort split with no omits.
            # This mostly happens to multiline strings that are by definition
            # reported as not fitting a single line, as well as lines that contain
            # trailing commas (those have to be exploded).
            yield from right_hand_split(
                line, line_length=mode.line_length, features=features
            )

        if mode.experimental_string_processing:
            if line.inside_brackets:
                transformers = [
                    string_merge,
                    string_paren_strip,
                    string_split,
                    delimiter_split,
                    standalone_comment_split,
                    string_paren_wrap,
                    rhs,
                ]
            else:
                transformers = [
                    string_merge,
                    string_paren_strip,
                    string_split,
                    string_paren_wrap,
                    rhs,
                ]
        else:
            if line.inside_brackets:
                transformers = [delimiter_split, standalone_comment_split, rhs]
            else:
                transformers = [rhs]

    for transform in transformers:
        # We are accumulating lines in `result` because we might want to abort
        # mission and return the original line in the end, or attempt a different
        # split altogether.
        try:
            result = run_transformer(line, transform, mode, features, line_str=line_str)
        except CannotTransform:
            continue
        else:
            yield from result
            break

    else:
        yield line


@dataclass  # type: ignore
class StringTransformer(ABC):
    """
    An implementation of the Transformer protocol that relies on its
    subclasses overriding the template methods `do_match(...)` and
    `do_transform(...)`.

    This Transformer works exclusively on strings (for example, by merging
    or splitting them).

    The following sections can be found among the docstrings of each concrete
    StringTransformer subclass.

    Requirements:
        Which requirements must be met of the given Line for this
        StringTransformer to be applied?

    Transformations:
        If the given Line meets all of the above requirements, which string
        transformations can you expect to be applied to it by this
        StringTransformer?

    Collaborations:
        What contractual agreements does this StringTransformer have with other
        StringTransfomers? Such collaborations should be eliminated/minimized
        as much as possible.
    """

    line_length: int
    normalize_strings: bool
    __name__ = "StringTransformer"

    @abstractmethod
    def do_match(self, line: Line) -> TMatchResult:
        """
        Returns:
            * Ok(string_idx) such that `line.leaves[string_idx]` is our target
            string, if a match was able to be made.
                OR
            * Err(CannotTransform), if a match was not able to be made.
        """

    @abstractmethod
    def do_transform(self, line: Line, string_idx: int) -> Iterator[TResult[Line]]:
        """
        Yields:
            * Ok(new_line) where new_line is the new transformed line.
                OR
            * Err(CannotTransform) if the transformation failed for some reason. The
            `do_match(...)` template method should usually be used to reject
            the form of the given Line, but in some cases it is difficult to
            know whether or not a Line meets the StringTransformer's
            requirements until the transformation is already midway.

        Side Effects:
            This method should NOT mutate @line directly, but it MAY mutate the
            Line's underlying Node structure. (WARNING: If the underlying Node
            structure IS altered, then this method should NOT be allowed to
            yield an CannotTransform after that point.)
        """

    def __call__(self, line: Line, _features: Collection[Feature]) -> Iterator[Line]:
        """
        StringTransformer instances have a call signature that mirrors that of
        the Transformer type.

        Raises:
            CannotTransform(...) if the concrete StringTransformer class is unable
            to transform @line.
        """
        # Optimization to avoid calling `self.do_match(...)` when the line does
        # not contain any string.
        if not any(leaf.type == token.STRING for leaf in line.leaves):
            raise CannotTransform("There are no strings in this line.")

        match_result = self.do_match(line)

        if isinstance(match_result, Err):
            cant_transform = match_result.err()
            raise CannotTransform(
                f"The string transformer {self.__class__.__name__} does not recognize"
                " this line as one that it can transform."
            ) from cant_transform

        string_idx = match_result.ok()

        for line_result in self.do_transform(line, string_idx):
            if isinstance(line_result, Err):
                cant_transform = line_result.err()
                raise CannotTransform(
                    "StringTransformer failed while attempting to transform string."
                ) from cant_transform
            line = line_result.ok()
            yield line


@dataclass
class CustomSplit:
    """A custom (i.e. manual) string split.

    A single CustomSplit instance represents a single substring.

    Examples:
        Consider the following string:
        ```
        "Hi there friend."
        " This is a custom"
        f" string {split}."
        ```

        This string will correspond to the following three CustomSplit instances:
        ```
        CustomSplit(False, 16)
        CustomSplit(False, 17)
        CustomSplit(True, 16)
        ```
    """

    has_prefix: bool
    break_idx: int


class CustomSplitMapMixin:
    """
    This mixin class is used to map merged strings to a sequence of
    CustomSplits, which will then be used to re-split the strings iff none of
    the resultant substrings go over the configured max line length.
    """

    _Key = Tuple[StringID, str]
    _CUSTOM_SPLIT_MAP: Dict[_Key, Tuple[CustomSplit, ...]] = defaultdict(tuple)

    @staticmethod
    def _get_key(string: str) -> "CustomSplitMapMixin._Key":
        """
        Returns:
            A unique identifier that is used internally to map @string to a
            group of custom splits.
        """
        return (id(string), string)

    def add_custom_splits(
        self, string: str, custom_splits: Iterable[CustomSplit]
    ) -> None:
        """Custom Split Map Setter Method

        Side Effects:
            Adds a mapping from @string to the custom splits @custom_splits.
        """
        key = self._get_key(string)
        self._CUSTOM_SPLIT_MAP[key] = tuple(custom_splits)

    def pop_custom_splits(self, string: str) -> List[CustomSplit]:
        """Custom Split Map Getter Method

        Returns:
            * A list of the custom splits that are mapped to @string, if any
            exist.
                OR
            * [], otherwise.

        Side Effects:
            Deletes the mapping between @string and its associated custom
            splits (which are returned to the caller).
        """
        key = self._get_key(string)

        custom_splits = self._CUSTOM_SPLIT_MAP[key]
        del self._CUSTOM_SPLIT_MAP[key]

        return list(custom_splits)

    def has_custom_splits(self, string: str) -> bool:
        """
        Returns:
            True iff @string is associated with a set of custom splits.
        """
        key = self._get_key(string)
        return key in self._CUSTOM_SPLIT_MAP


class StringMerger(CustomSplitMapMixin, StringTransformer):
    """StringTransformer that merges strings together.

    Requirements:
        (A) The line contains adjacent strings such that ALL of the validation checks
        listed in StringMerger.__validate_msg(...)'s docstring pass.
            OR
        (B) The line contains a string which uses line continuation backslashes.

    Transformations:
        Depending on which of the two requirements above where met, either:

        (A) The string group associated with the target string is merged.
            OR
        (B) All line-continuation backslashes are removed from the target string.

    Collaborations:
        StringMerger provides custom split information to StringSplitter.
    """

    def do_match(self, line: Line) -> TMatchResult:
        LL = line.leaves

        is_valid_index = is_valid_index_factory(LL)

        for (i, leaf) in enumerate(LL):
            if (
                leaf.type == token.STRING
                and is_valid_index(i + 1)
                and LL[i + 1].type == token.STRING
            ):
                return Ok(i)

            if leaf.type == token.STRING and "\\\n" in leaf.value:
                return Ok(i)

        return TErr("This line has no strings that need merging.")

    def do_transform(self, line: Line, string_idx: int) -> Iterator[TResult[Line]]:
        new_line = line
        rblc_result = self.__remove_backslash_line_continuation_chars(
            new_line, string_idx
        )
        if isinstance(rblc_result, Ok):
            new_line = rblc_result.ok()

        msg_result = self.__merge_string_group(new_line, string_idx)
        if isinstance(msg_result, Ok):
            new_line = msg_result.ok()

        if isinstance(rblc_result, Err) and isinstance(msg_result, Err):
            msg_cant_transform = msg_result.err()
            rblc_cant_transform = rblc_result.err()
            cant_transform = CannotTransform(
                "StringMerger failed to merge any strings in this line."
            )

            # Chain the errors together using `__cause__`.
            msg_cant_transform.__cause__ = rblc_cant_transform
            cant_transform.__cause__ = msg_cant_transform

            yield Err(cant_transform)
        else:
            yield Ok(new_line)

    @staticmethod
    def __remove_backslash_line_continuation_chars(
        line: Line, string_idx: int
    ) -> TResult[Line]:
        """
        Merge strings that were split across multiple lines using
        line-continuation backslashes.

        Returns:
            Ok(new_line), if @line contains backslash line-continuation
            characters.
                OR
            Err(CannotTransform), otherwise.
        """
        LL = line.leaves

        string_leaf = LL[string_idx]
        if not (
            string_leaf.type == token.STRING
            and "\\\n" in string_leaf.value
            and not has_triple_quotes(string_leaf.value)
        ):
            return TErr(
                f"String leaf {string_leaf} does not contain any backslash line"
                " continuation characters."
            )

        new_line = line.clone()
        new_line.comments = line.comments.copy()
        append_leaves(new_line, line, LL)

        new_string_leaf = new_line.leaves[string_idx]
        new_string_leaf.value = new_string_leaf.value.replace("\\\n", "")

        return Ok(new_line)

    def __merge_string_group(self, line: Line, string_idx: int) -> TResult[Line]:
        """
        Merges string group (i.e. set of adjacent strings) where the first
        string in the group is `line.leaves[string_idx]`.

        Returns:
            Ok(new_line), if ALL of the validation checks found in
            __validate_msg(...) pass.
                OR
            Err(CannotTransform), otherwise.
        """
        LL = line.leaves

        is_valid_index = is_valid_index_factory(LL)

        vresult = self.__validate_msg(line, string_idx)
        if isinstance(vresult, Err):
            return vresult

        # If the string group is wrapped inside an Atom node, we must make sure
        # to later replace that Atom with our new (merged) string leaf.
        atom_node = LL[string_idx].parent

        # We will place BREAK_MARK in between every two substrings that we
        # merge. We will then later go through our final result and use the
        # various instances of BREAK_MARK we find to add the right values to
        # the custom split map.
        BREAK_MARK = "@@@@@ BLACK BREAKPOINT MARKER @@@@@"

        QUOTE = LL[string_idx].value[-1]

        def make_naked(string: str, string_prefix: str) -> str:
            """Strip @string (i.e. make it a "naked" string)

            Pre-conditions:
                * assert_is_leaf_string(@string)

            Returns:
                A string that is identical to @string except that
                @string_prefix has been stripped, the surrounding QUOTE
                characters have been removed, and any remaining QUOTE
                characters have been escaped.
            """
            assert_is_leaf_string(string)

            RE_EVEN_BACKSLASHES = r"(?:(?<!\\)(?:\\\\)*)"
            naked_string = string[len(string_prefix) + 1 : -1]
            naked_string = re.sub(
                "(" + RE_EVEN_BACKSLASHES + ")" + QUOTE, r"\1\\" + QUOTE, naked_string
            )
            return naked_string

        # Holds the CustomSplit objects that will later be added to the custom
        # split map.
        custom_splits = []

        # Temporary storage for the 'has_prefix' part of the CustomSplit objects.
        prefix_tracker = []

        # Sets the 'prefix' variable. This is the prefix that the final merged
        # string will have.
        next_str_idx = string_idx
        prefix = ""
        while (
            not prefix
            and is_valid_index(next_str_idx)
            and LL[next_str_idx].type == token.STRING
        ):
            prefix = get_string_prefix(LL[next_str_idx].value)
            next_str_idx += 1

        # The next loop merges the string group. The final string will be
        # contained in 'S'.
        #
        # The following convenience variables are used:
        #
        #   S: string
        #   NS: naked string
        #   SS: next string
        #   NSS: naked next string
        S = ""
        NS = ""
        num_of_strings = 0
        next_str_idx = string_idx
        while is_valid_index(next_str_idx) and LL[next_str_idx].type == token.STRING:
            num_of_strings += 1

            SS = LL[next_str_idx].value
            next_prefix = get_string_prefix(SS)

            # If this is an f-string group but this substring is not prefixed
            # with 'f'...
            if "f" in prefix and "f" not in next_prefix:
                # Then we must escape any braces contained in this substring.
                SS = re.subf(r"(\{|\})", "{1}{1}", SS)

            NSS = make_naked(SS, next_prefix)

            has_prefix = bool(next_prefix)
            prefix_tracker.append(has_prefix)

            S = prefix + QUOTE + NS + NSS + BREAK_MARK + QUOTE
            NS = make_naked(S, prefix)

            next_str_idx += 1

        S_leaf = Leaf(token.STRING, S)
        if self.normalize_strings:
            normalize_string_quotes(S_leaf)

        # Fill the 'custom_splits' list with the appropriate CustomSplit objects.
        temp_string = S_leaf.value[len(prefix) + 1 : -1]
        for has_prefix in prefix_tracker:
            mark_idx = temp_string.find(BREAK_MARK)
            assert (
                mark_idx >= 0
            ), "Logic error while filling the custom string breakpoint cache."

            temp_string = temp_string[mark_idx + len(BREAK_MARK) :]
            breakpoint_idx = mark_idx + (len(prefix) if has_prefix else 0) + 1
            custom_splits.append(CustomSplit(has_prefix, breakpoint_idx))

        string_leaf = Leaf(token.STRING, S_leaf.value.replace(BREAK_MARK, ""))

        if atom_node is not None:
            replace_child(atom_node, string_leaf)

        # Build the final line ('new_line') that this method will later return.
        new_line = line.clone()
        for (i, leaf) in enumerate(LL):
            if i == string_idx:
                new_line.append(string_leaf)

            if string_idx <= i < string_idx + num_of_strings:
                for comment_leaf in line.comments_after(LL[i]):
                    new_line.append(comment_leaf, preformatted=True)
                continue

            append_leaves(new_line, line, [leaf])

        self.add_custom_splits(string_leaf.value, custom_splits)
        return Ok(new_line)

    @staticmethod
    def __validate_msg(line: Line, string_idx: int) -> TResult[None]:
        """Validate (M)erge (S)tring (G)roup

        Transform-time string validation logic for __merge_string_group(...).

        Returns:
            * Ok(None), if ALL validation checks (listed below) pass.
                OR
            * Err(CannotTransform), if any of the following are true:
                - The target string group does not contain ANY stand-alone comments.
                - The target string is not in a string group (i.e. it has no
                  adjacent strings).
                - The string group has more than one inline comment.
                - The string group has an inline comment that appears to be a pragma.
                - The set of all string prefixes in the string group is of
                  length greater than one and is not equal to {"", "f"}.
                - The string group consists of raw strings.
        """
        # We first check for "inner" stand-alone comments (i.e. stand-alone
        # comments that have a string leaf before them AND after them).
        for inc in [1, -1]:
            i = string_idx
            found_sa_comment = False
            is_valid_index = is_valid_index_factory(line.leaves)
            while is_valid_index(i) and line.leaves[i].type in [
                token.STRING,
                STANDALONE_COMMENT,
            ]:
                if line.leaves[i].type == STANDALONE_COMMENT:
                    found_sa_comment = True
                elif found_sa_comment:
                    return TErr(
                        "StringMerger does NOT merge string groups which contain "
                        "stand-alone comments."
                    )

                i += inc

        num_of_inline_string_comments = 0
        set_of_prefixes = set()
        num_of_strings = 0
        for leaf in line.leaves[string_idx:]:
            if leaf.type != token.STRING:
                # If the string group is trailed by a comma, we count the
                # comments trailing the comma to be one of the string group's
                # comments.
                if leaf.type == token.COMMA and id(leaf) in line.comments:
                    num_of_inline_string_comments += 1
                break

            if has_triple_quotes(leaf.value):
                return TErr("StringMerger does NOT merge multiline strings.")

            num_of_strings += 1
            prefix = get_string_prefix(leaf.value)
            if "r" in prefix:
                return TErr("StringMerger does NOT merge raw strings.")

            set_of_prefixes.add(prefix)

            if id(leaf) in line.comments:
                num_of_inline_string_comments += 1
                if contains_pragma_comment(line.comments[id(leaf)]):
                    return TErr("Cannot merge strings which have pragma comments.")

        if num_of_strings < 2:
            return TErr(
                f"Not enough strings to merge (num_of_strings={num_of_strings})."
            )

        if num_of_inline_string_comments > 1:
            return TErr(
                f"Too many inline string comments ({num_of_inline_string_comments})."
            )

        if len(set_of_prefixes) > 1 and set_of_prefixes != {"", "f"}:
            return TErr(f"Too many different prefixes ({set_of_prefixes}).")

        return Ok(None)


class StringParenStripper(StringTransformer):
    """StringTransformer that strips surrounding parentheses from strings.

    Requirements:
        The line contains a string which is surrounded by parentheses and:
            - The target string is NOT the only argument to a function call.
            - The target string is NOT a "pointless" string.
            - If the target string contains a PERCENT, the brackets are not
              preceeded or followed by an operator with higher precedence than
              PERCENT.

    Transformations:
        The parentheses mentioned in the 'Requirements' section are stripped.

    Collaborations:
        StringParenStripper has its own inherent usefulness, but it is also
        relied on to clean up the parentheses created by StringParenWrapper (in
        the event that they are no longer needed).
    """

    def do_match(self, line: Line) -> TMatchResult:
        LL = line.leaves

        is_valid_index = is_valid_index_factory(LL)

        for (idx, leaf) in enumerate(LL):
            # Should be a string...
            if leaf.type != token.STRING:
                continue

            # If this is a "pointless" string...
            if (
                leaf.parent
                and leaf.parent.parent
                and leaf.parent.parent.type == syms.simple_stmt
            ):
                continue

            # Should be preceded by a non-empty LPAR...
            if (
                not is_valid_index(idx - 1)
                or LL[idx - 1].type != token.LPAR
                or is_empty_lpar(LL[idx - 1])
            ):
                continue

            # That LPAR should NOT be preceded by a function name or a closing
            # bracket (which could be a function which returns a function or a
            # list/dictionary that contains a function)...
            if is_valid_index(idx - 2) and (
                LL[idx - 2].type == token.NAME or LL[idx - 2].type in CLOSING_BRACKETS
            ):
                continue

            string_idx = idx

            # Skip the string trailer, if one exists.
            string_parser = StringParser()
            next_idx = string_parser.parse(LL, string_idx)

            # if the leaves in the parsed string include a PERCENT, we need to
            # make sure the initial LPAR is NOT preceded by an operator with
            # higher or equal precedence to PERCENT
            if is_valid_index(idx - 2):
                # mypy can't quite follow unless we name this
                before_lpar = LL[idx - 2]
                if token.PERCENT in {leaf.type for leaf in LL[idx - 1 : next_idx]} and (
                    (
                        before_lpar.type
                        in {
                            token.STAR,
                            token.AT,
                            token.SLASH,
                            token.DOUBLESLASH,
                            token.PERCENT,
                            token.TILDE,
                            token.DOUBLESTAR,
                            token.AWAIT,
                            token.LSQB,
                            token.LPAR,
                        }
                    )
                    or (
                        # only unary PLUS/MINUS
                        before_lpar.parent
                        and before_lpar.parent.type == syms.factor
                        and (before_lpar.type in {token.PLUS, token.MINUS})
                    )
                ):
                    continue

            # Should be followed by a non-empty RPAR...
            if (
                is_valid_index(next_idx)
                and LL[next_idx].type == token.RPAR
                and not is_empty_rpar(LL[next_idx])
            ):
                # That RPAR should NOT be followed by anything with higher
                # precedence than PERCENT
                if is_valid_index(next_idx + 1) and LL[next_idx + 1].type in {
                    token.DOUBLESTAR,
                    token.LSQB,
                    token.LPAR,
                    token.DOT,
                }:
                    continue

                return Ok(string_idx)

        return TErr("This line has no strings wrapped in parens.")

    def do_transform(self, line: Line, string_idx: int) -> Iterator[TResult[Line]]:
        LL = line.leaves

        string_parser = StringParser()
        rpar_idx = string_parser.parse(LL, string_idx)

        for leaf in (LL[string_idx - 1], LL[rpar_idx]):
            if line.comments_after(leaf):
                yield TErr(
                    "Will not strip parentheses which have comments attached to them."
                )
                return

        new_line = line.clone()
        new_line.comments = line.comments.copy()
        try:
            append_leaves(new_line, line, LL[: string_idx - 1])
        except BracketMatchError:
            # HACK: I believe there is currently a bug somewhere in
            # right_hand_split() that is causing brackets to not be tracked
            # properly by a shared BracketTracker.
            append_leaves(new_line, line, LL[: string_idx - 1], preformatted=True)

        string_leaf = Leaf(token.STRING, LL[string_idx].value)
        LL[string_idx - 1].remove()
        replace_child(LL[string_idx], string_leaf)
        new_line.append(string_leaf)

        append_leaves(
            new_line, line, LL[string_idx + 1 : rpar_idx] + LL[rpar_idx + 1 :]
        )

        LL[rpar_idx].remove()

        yield Ok(new_line)


class BaseStringSplitter(StringTransformer):
    """
    Abstract class for StringTransformers which transform a Line's strings by splitting
    them or placing them on their own lines where necessary to avoid going over
    the configured line length.

    Requirements:
        * The target string value is responsible for the line going over the
        line length limit. It follows that after all of black's other line
        split methods have been exhausted, this line (or one of the resulting
        lines after all line splits are performed) would still be over the
        line_length limit unless we split this string.
            AND
        * The target string is NOT a "pointless" string (i.e. a string that has
        no parent or siblings).
            AND
        * The target string is not followed by an inline comment that appears
        to be a pragma.
            AND
        * The target string is not a multiline (i.e. triple-quote) string.
    """

    @abstractmethod
    def do_splitter_match(self, line: Line) -> TMatchResult:
        """
        BaseStringSplitter asks its clients to override this method instead of
        `StringTransformer.do_match(...)`.

        Follows the same protocol as `StringTransformer.do_match(...)`.

        Refer to `help(StringTransformer.do_match)` for more information.
        """

    def do_match(self, line: Line) -> TMatchResult:
        match_result = self.do_splitter_match(line)
        if isinstance(match_result, Err):
            return match_result

        string_idx = match_result.ok()
        vresult = self.__validate(line, string_idx)
        if isinstance(vresult, Err):
            return vresult

        return match_result

    def __validate(self, line: Line, string_idx: int) -> TResult[None]:
        """
        Checks that @line meets all of the requirements listed in this classes'
        docstring. Refer to `help(BaseStringSplitter)` for a detailed
        description of those requirements.

        Returns:
            * Ok(None), if ALL of the requirements are met.
                OR
            * Err(CannotTransform), if ANY of the requirements are NOT met.
        """
        LL = line.leaves

        string_leaf = LL[string_idx]

        max_string_length = self.__get_max_string_length(line, string_idx)
        if len(string_leaf.value) <= max_string_length:
            return TErr(
                "The string itself is not what is causing this line to be too long."
            )

        if not string_leaf.parent or [L.type for L in string_leaf.parent.children] == [
            token.STRING,
            token.NEWLINE,
        ]:
            return TErr(
                f"This string ({string_leaf.value}) appears to be pointless (i.e. has"
                " no parent)."
            )

        if id(line.leaves[string_idx]) in line.comments and contains_pragma_comment(
            line.comments[id(line.leaves[string_idx])]
        ):
            return TErr(
                "Line appears to end with an inline pragma comment. Splitting the line"
                " could modify the pragma's behavior."
            )

        if has_triple_quotes(string_leaf.value):
            return TErr("We cannot split multiline strings.")

        return Ok(None)

    def __get_max_string_length(self, line: Line, string_idx: int) -> int:
        """
        Calculates the max string length used when attempting to determine
        whether or not the target string is responsible for causing the line to
        go over the line length limit.

        WARNING: This method is tightly coupled to both StringSplitter and
        (especially) StringParenWrapper. There is probably a better way to
        accomplish what is being done here.

        Returns:
            max_string_length: such that `line.leaves[string_idx].value >
            max_string_length` implies that the target string IS responsible
            for causing this line to exceed the line length limit.
        """
        LL = line.leaves

        is_valid_index = is_valid_index_factory(LL)

        # We use the shorthand "WMA4" in comments to abbreviate "We must
        # account for". When giving examples, we use STRING to mean some/any
        # valid string.
        #
        # Finally, we use the following convenience variables:
        #
        #   P:  The leaf that is before the target string leaf.
        #   N:  The leaf that is after the target string leaf.
        #   NN: The leaf that is after N.

        # WMA4 the whitespace at the beginning of the line.
        offset = line.depth * 4

        if is_valid_index(string_idx - 1):
            p_idx = string_idx - 1
            if (
                LL[string_idx - 1].type == token.LPAR
                and LL[string_idx - 1].value == ""
                and string_idx >= 2
            ):
                # If the previous leaf is an empty LPAR placeholder, we should skip it.
                p_idx -= 1

            P = LL[p_idx]
            if P.type == token.PLUS:
                # WMA4 a space and a '+' character (e.g. `+ STRING`).
                offset += 2

            if P.type == token.COMMA:
                # WMA4 a space, a comma, and a closing bracket [e.g. `), STRING`].
                offset += 3

            if P.type in [token.COLON, token.EQUAL, token.NAME]:
                # This conditional branch is meant to handle dictionary keys,
                # variable assignments, 'return STRING' statement lines, and
                # 'else STRING' ternary expression lines.

                # WMA4 a single space.
                offset += 1

                # WMA4 the lengths of any leaves that came before that space,
                # but after any closing bracket before that space.
                for leaf in reversed(LL[: p_idx + 1]):
                    offset += len(str(leaf))
                    if leaf.type in CLOSING_BRACKETS:
                        break

        if is_valid_index(string_idx + 1):
            N = LL[string_idx + 1]
            if N.type == token.RPAR and N.value == "" and len(LL) > string_idx + 2:
                # If the next leaf is an empty RPAR placeholder, we should skip it.
                N = LL[string_idx + 2]

            if N.type == token.COMMA:
                # WMA4 a single comma at the end of the string (e.g `STRING,`).
                offset += 1

            if is_valid_index(string_idx + 2):
                NN = LL[string_idx + 2]

                if N.type == token.DOT and NN.type == token.NAME:
                    # This conditional branch is meant to handle method calls invoked
                    # off of a string literal up to and including the LPAR character.

                    # WMA4 the '.' character.
                    offset += 1

                    if (
                        is_valid_index(string_idx + 3)
                        and LL[string_idx + 3].type == token.LPAR
                    ):
                        # WMA4 the left parenthesis character.
                        offset += 1

                    # WMA4 the length of the method's name.
                    offset += len(NN.value)

        has_comments = False
        for comment_leaf in line.comments_after(LL[string_idx]):
            if not has_comments:
                has_comments = True
                # WMA4 two spaces before the '#' character.
                offset += 2

            # WMA4 the length of the inline comment.
            offset += len(comment_leaf.value)

        max_string_length = self.line_length - offset
        return max_string_length


class StringSplitter(CustomSplitMapMixin, BaseStringSplitter):
    """
    StringTransformer that splits "atom" strings (i.e. strings which exist on
    lines by themselves).

    Requirements:
        * The line consists ONLY of a single string (with the exception of a
        '+' symbol which MAY exist at the start of the line), MAYBE a string
        trailer, and MAYBE a trailing comma.
            AND
        * All of the requirements listed in BaseStringSplitter's docstring.

    Transformations:
        The string mentioned in the 'Requirements' section is split into as
        many substrings as necessary to adhere to the configured line length.

        In the final set of substrings, no substring should be smaller than
        MIN_SUBSTR_SIZE characters.

        The string will ONLY be split on spaces (i.e. each new substring should
        start with a space). Note that the string will NOT be split on a space
        which is escaped with a backslash.

        If the string is an f-string, it will NOT be split in the middle of an
        f-expression (e.g. in f"FooBar: {foo() if x else bar()}", {foo() if x
        else bar()} is an f-expression).

        If the string that is being split has an associated set of custom split
        records and those custom splits will NOT result in any line going over
        the configured line length, those custom splits are used. Otherwise the
        string is split as late as possible (from left-to-right) while still
        adhering to the transformation rules listed above.

    Collaborations:
        StringSplitter relies on StringMerger to construct the appropriate
        CustomSplit objects and add them to the custom split map.
    """

    MIN_SUBSTR_SIZE = 6
    # Matches an "f-expression" (e.g. {var}) that might be found in an f-string.
    RE_FEXPR = r"""
    (?<!\{) (?:\{\{)* \{ (?!\{)
        (?:
            [^\{\}]
            | \{\{
            | \}\}
            | (?R)
        )+?
    (?<!\}) \} (?:\}\})* (?!\})
    """

    def do_splitter_match(self, line: Line) -> TMatchResult:
        LL = line.leaves

        is_valid_index = is_valid_index_factory(LL)

        idx = 0

        # The first leaf MAY be a '+' symbol...
        if is_valid_index(idx) and LL[idx].type == token.PLUS:
            idx += 1

        # The next/first leaf MAY be an empty LPAR...
        if is_valid_index(idx) and is_empty_lpar(LL[idx]):
            idx += 1

        # The next/first leaf MUST be a string...
        if not is_valid_index(idx) or LL[idx].type != token.STRING:
            return TErr("Line does not start with a string.")

        string_idx = idx

        # Skip the string trailer, if one exists.
        string_parser = StringParser()
        idx = string_parser.parse(LL, string_idx)

        # That string MAY be followed by an empty RPAR...
        if is_valid_index(idx) and is_empty_rpar(LL[idx]):
            idx += 1

        # That string / empty RPAR leaf MAY be followed by a comma...
        if is_valid_index(idx) and LL[idx].type == token.COMMA:
            idx += 1

        # But no more leaves are allowed...
        if is_valid_index(idx):
            return TErr("This line does not end with a string.")

        return Ok(string_idx)

    def do_transform(self, line: Line, string_idx: int) -> Iterator[TResult[Line]]:
        LL = line.leaves

        QUOTE = LL[string_idx].value[-1]

        is_valid_index = is_valid_index_factory(LL)
        insert_str_child = insert_str_child_factory(LL[string_idx])

        prefix = get_string_prefix(LL[string_idx].value)

        # We MAY choose to drop the 'f' prefix from substrings that don't
        # contain any f-expressions, but ONLY if the original f-string
        # contains at least one f-expression. Otherwise, we will alter the AST
        # of the program.
        drop_pointless_f_prefix = ("f" in prefix) and re.search(
            self.RE_FEXPR, LL[string_idx].value, re.VERBOSE
        )

        first_string_line = True
        starts_with_plus = LL[0].type == token.PLUS

        def line_needs_plus() -> bool:
            return first_string_line and starts_with_plus

        def maybe_append_plus(new_line: Line) -> None:
            """
            Side Effects:
                If @line starts with a plus and this is the first line we are
                constructing, this function appends a PLUS leaf to @new_line
                and replaces the old PLUS leaf in the node structure. Otherwise
                this function does nothing.
            """
            if line_needs_plus():
                plus_leaf = Leaf(token.PLUS, "+")
                replace_child(LL[0], plus_leaf)
                new_line.append(plus_leaf)

        ends_with_comma = (
            is_valid_index(string_idx + 1) and LL[string_idx + 1].type == token.COMMA
        )

        def max_last_string() -> int:
            """
            Returns:
                The max allowed length of the string value used for the last
                line we will construct.
            """
            result = self.line_length
            result -= line.depth * 4
            result -= 1 if ends_with_comma else 0
            result -= 2 if line_needs_plus() else 0
            return result

        # --- Calculate Max Break Index (for string value)
        # We start with the line length limit
        max_break_idx = self.line_length
        # The last index of a string of length N is N-1.
        max_break_idx -= 1
        # Leading whitespace is not present in the string value (e.g. Leaf.value).
        max_break_idx -= line.depth * 4
        if max_break_idx < 0:
            yield TErr(
                f"Unable to split {LL[string_idx].value} at such high of a line depth:"
                f" {line.depth}"
            )
            return

        # Check if StringMerger registered any custom splits.
        custom_splits = self.pop_custom_splits(LL[string_idx].value)
        # We use them ONLY if none of them would produce lines that exceed the
        # line limit.
        use_custom_breakpoints = bool(
            custom_splits
            and all(csplit.break_idx <= max_break_idx for csplit in custom_splits)
        )

        # Temporary storage for the remaining chunk of the string line that
        # can't fit onto the line currently being constructed.
        rest_value = LL[string_idx].value

        def more_splits_should_be_made() -> bool:
            """
            Returns:
                True iff `rest_value` (the remaining string value from the last
                split), should be split again.
            """
            if use_custom_breakpoints:
                return len(custom_splits) > 1
            else:
                return len(rest_value) > max_last_string()

        string_line_results: List[Ok[Line]] = []
        while more_splits_should_be_made():
            if use_custom_breakpoints:
                # Custom User Split (manual)
                csplit = custom_splits.pop(0)
                break_idx = csplit.break_idx
            else:
                # Algorithmic Split (automatic)
                max_bidx = max_break_idx - 2 if line_needs_plus() else max_break_idx
                maybe_break_idx = self.__get_break_idx(rest_value, max_bidx)
                if maybe_break_idx is None:
                    # If we are unable to algorithmically determine a good split
                    # and this string has custom splits registered to it, we
                    # fall back to using them--which means we have to start
                    # over from the beginning.
                    if custom_splits:
                        rest_value = LL[string_idx].value
                        string_line_results = []
                        first_string_line = True
                        use_custom_breakpoints = True
                        continue

                    # Otherwise, we stop splitting here.
                    break

                break_idx = maybe_break_idx

            # --- Construct `next_value`
            next_value = rest_value[:break_idx] + QUOTE
            if (
                # Are we allowed to try to drop a pointless 'f' prefix?
                drop_pointless_f_prefix
                # If we are, will we be successful?
                and next_value != self.__normalize_f_string(next_value, prefix)
            ):
                # If the current custom split did NOT originally use a prefix,
                # then `csplit.break_idx` will be off by one after removing
                # the 'f' prefix.
                break_idx = (
                    break_idx + 1
                    if use_custom_breakpoints and not csplit.has_prefix
                    else break_idx
                )
                next_value = rest_value[:break_idx] + QUOTE
                next_value = self.__normalize_f_string(next_value, prefix)

            # --- Construct `next_leaf`
            next_leaf = Leaf(token.STRING, next_value)
            insert_str_child(next_leaf)
            self.__maybe_normalize_string_quotes(next_leaf)

            # --- Construct `next_line`
            next_line = line.clone()
            maybe_append_plus(next_line)
            next_line.append(next_leaf)
            string_line_results.append(Ok(next_line))

            rest_value = prefix + QUOTE + rest_value[break_idx:]
            first_string_line = False

        yield from string_line_results

        if drop_pointless_f_prefix:
            rest_value = self.__normalize_f_string(rest_value, prefix)

        rest_leaf = Leaf(token.STRING, rest_value)
        insert_str_child(rest_leaf)

        # NOTE: I could not find a test case that verifies that the following
        # line is actually necessary, but it seems to be. Otherwise we risk
        # not normalizing the last substring, right?
        self.__maybe_normalize_string_quotes(rest_leaf)

        last_line = line.clone()
        maybe_append_plus(last_line)

        # If there are any leaves to the right of the target string...
        if is_valid_index(string_idx + 1):
            # We use `temp_value` here to determine how long the last line
            # would be if we were to append all the leaves to the right of the
            # target string to the last string line.
            temp_value = rest_value
            for leaf in LL[string_idx + 1 :]:
                temp_value += str(leaf)
                if leaf.type == token.LPAR:
                    break

            # Try to fit them all on the same line with the last substring...
            if (
                len(temp_value) <= max_last_string()
                or LL[string_idx + 1].type == token.COMMA
            ):
                last_line.append(rest_leaf)
                append_leaves(last_line, line, LL[string_idx + 1 :])
                yield Ok(last_line)
            # Otherwise, place the last substring on one line and everything
            # else on a line below that...
            else:
                last_line.append(rest_leaf)
                yield Ok(last_line)

                non_string_line = line.clone()
                append_leaves(non_string_line, line, LL[string_idx + 1 :])
                yield Ok(non_string_line)
        # Else the target string was the last leaf...
        else:
            last_line.append(rest_leaf)
            last_line.comments = line.comments.copy()
            yield Ok(last_line)

    def __get_break_idx(self, string: str, max_break_idx: int) -> Optional[int]:
        """
        This method contains the algorithm that StringSplitter uses to
        determine which character to split each string at.

        Args:
            @string: The substring that we are attempting to split.
            @max_break_idx: The ideal break index. We will return this value if it
            meets all the necessary conditions. In the likely event that it
            doesn't we will try to find the closest index BELOW @max_break_idx
            that does. If that fails, we will expand our search by also
            considering all valid indices ABOVE @max_break_idx.

        Pre-Conditions:
            * assert_is_leaf_string(@string)
            * 0 <= @max_break_idx < len(@string)

        Returns:
            break_idx, if an index is able to be found that meets all of the
            conditions listed in the 'Transformations' section of this classes'
            docstring.
                OR
            None, otherwise.
        """
        is_valid_index = is_valid_index_factory(string)

        assert is_valid_index(max_break_idx)
        assert_is_leaf_string(string)

        _fexpr_slices: Optional[List[Tuple[Index, Index]]] = None

        def fexpr_slices() -> Iterator[Tuple[Index, Index]]:
            """
            Yields:
                All ranges of @string which, if @string were to be split there,
                would result in the splitting of an f-expression (which is NOT
                allowed).
            """
            nonlocal _fexpr_slices

            if _fexpr_slices is None:
                _fexpr_slices = []
                for match in re.finditer(self.RE_FEXPR, string, re.VERBOSE):
                    _fexpr_slices.append(match.span())

            yield from _fexpr_slices

        is_fstring = "f" in get_string_prefix(string)

        def breaks_fstring_expression(i: Index) -> bool:
            """
            Returns:
                True iff returning @i would result in the splitting of an
                f-expression (which is NOT allowed).
            """
            if not is_fstring:
                return False

            for (start, end) in fexpr_slices():
                if start <= i < end:
                    return True

            return False

        def passes_all_checks(i: Index) -> bool:
            """
            Returns:
                True iff ALL of the conditions listed in the 'Transformations'
                section of this classes' docstring would be be met by returning @i.
            """
            is_space = string[i] == " "

            is_not_escaped = True
            j = i - 1
            while is_valid_index(j) and string[j] == "\\":
                is_not_escaped = not is_not_escaped
                j -= 1

            is_big_enough = (
                len(string[i:]) >= self.MIN_SUBSTR_SIZE
                and len(string[:i]) >= self.MIN_SUBSTR_SIZE
            )
            return (
                is_space
                and is_not_escaped
                and is_big_enough
                and not breaks_fstring_expression(i)
            )

        # First, we check all indices BELOW @max_break_idx.
        break_idx = max_break_idx
        while is_valid_index(break_idx - 1) and not passes_all_checks(break_idx):
            break_idx -= 1

        if not passes_all_checks(break_idx):
            # If that fails, we check all indices ABOVE @max_break_idx.
            #
            # If we are able to find a valid index here, the next line is going
            # to be longer than the specified line length, but it's probably
            # better than doing nothing at all.
            break_idx = max_break_idx + 1
            while is_valid_index(break_idx + 1) and not passes_all_checks(break_idx):
                break_idx += 1

            if not is_valid_index(break_idx) or not passes_all_checks(break_idx):
                return None

        return break_idx

    def __maybe_normalize_string_quotes(self, leaf: Leaf) -> None:
        if self.normalize_strings:
            normalize_string_quotes(leaf)

    def __normalize_f_string(self, string: str, prefix: str) -> str:
        """
        Pre-Conditions:
            * assert_is_leaf_string(@string)

        Returns:
            * If @string is an f-string that contains no f-expressions, we
            return a string identical to @string except that the 'f' prefix
            has been stripped and all double braces (i.e. '{{' or '}}') have
            been normalized (i.e. turned into '{' or '}').
                OR
            * Otherwise, we return @string.
        """
        assert_is_leaf_string(string)

        if "f" in prefix and not re.search(self.RE_FEXPR, string, re.VERBOSE):
            new_prefix = prefix.replace("f", "")

            temp = string[len(prefix) :]
            temp = re.sub(r"\{\{", "{", temp)
            temp = re.sub(r"\}\}", "}", temp)
            new_string = temp

            return f"{new_prefix}{new_string}"
        else:
            return string


class StringParenWrapper(CustomSplitMapMixin, BaseStringSplitter):
    """
    StringTransformer that splits non-"atom" strings (i.e. strings that do not
    exist on lines by themselves).

    Requirements:
        All of the requirements listed in BaseStringSplitter's docstring in
        addition to the requirements listed below:

        * The line is a return/yield statement, which returns/yields a string.
            OR
        * The line is part of a ternary expression (e.g. `x = y if cond else
        z`) such that the line starts with `else <string>`, where <string> is
        some string.
            OR
        * The line is an assert statement, which ends with a string.
            OR
        * The line is an assignment statement (e.g. `x = <string>` or `x +=
        <string>`) such that the variable is being assigned the value of some
        string.
            OR
        * The line is a dictionary key assignment where some valid key is being
        assigned the value of some string.

    Transformations:
        The chosen string is wrapped in parentheses and then split at the LPAR.

        We then have one line which ends with an LPAR and another line that
        starts with the chosen string. The latter line is then split again at
        the RPAR. This results in the RPAR (and possibly a trailing comma)
        being placed on its own line.

        NOTE: If any leaves exist to the right of the chosen string (except
        for a trailing comma, which would be placed after the RPAR), those
        leaves are placed inside the parentheses.  In effect, the chosen
        string is not necessarily being "wrapped" by parentheses. We can,
        however, count on the LPAR being placed directly before the chosen
        string.

        In other words, StringParenWrapper creates "atom" strings. These
        can then be split again by StringSplitter, if necessary.

    Collaborations:
        In the event that a string line split by StringParenWrapper is
        changed such that it no longer needs to be given its own line,
        StringParenWrapper relies on StringParenStripper to clean up the
        parentheses it created.
    """

    def do_splitter_match(self, line: Line) -> TMatchResult:
        LL = line.leaves

        string_idx = (
            self._return_match(LL)
            or self._else_match(LL)
            or self._assert_match(LL)
            or self._assign_match(LL)
            or self._dict_match(LL)
        )

        if string_idx is not None:
            string_value = line.leaves[string_idx].value
            # If the string has no spaces...
            if " " not in string_value:
                # And will still violate the line length limit when split...
                max_string_length = self.line_length - ((line.depth + 1) * 4)
                if len(string_value) > max_string_length:
                    # And has no associated custom splits...
                    if not self.has_custom_splits(string_value):
                        # Then we should NOT put this string on its own line.
                        return TErr(
                            "We do not wrap long strings in parentheses when the"
                            " resultant line would still be over the specified line"
                            " length and can't be split further by StringSplitter."
                        )
            return Ok(string_idx)

        return TErr("This line does not contain any non-atomic strings.")

    @staticmethod
    def _return_match(LL: List[Leaf]) -> Optional[int]:
        """
        Returns:
            string_idx such that @LL[string_idx] is equal to our target (i.e.
            matched) string, if this line matches the return/yield statement
            requirements listed in the 'Requirements' section of this classes'
            docstring.
                OR
            None, otherwise.
        """
        # If this line is apart of a return/yield statement and the first leaf
        # contains either the "return" or "yield" keywords...
        if parent_type(LL[0]) in [syms.return_stmt, syms.yield_expr] and LL[
            0
        ].value in ["return", "yield"]:
            is_valid_index = is_valid_index_factory(LL)

            idx = 2 if is_valid_index(1) and is_empty_par(LL[1]) else 1
            # The next visible leaf MUST contain a string...
            if is_valid_index(idx) and LL[idx].type == token.STRING:
                return idx

        return None

    @staticmethod
    def _else_match(LL: List[Leaf]) -> Optional[int]:
        """
        Returns:
            string_idx such that @LL[string_idx] is equal to our target (i.e.
            matched) string, if this line matches the ternary expression
            requirements listed in the 'Requirements' section of this classes'
            docstring.
                OR
            None, otherwise.
        """
        # If this line is apart of a ternary expression and the first leaf
        # contains the "else" keyword...
        if (
            parent_type(LL[0]) == syms.test
            and LL[0].type == token.NAME
            and LL[0].value == "else"
        ):
            is_valid_index = is_valid_index_factory(LL)

            idx = 2 if is_valid_index(1) and is_empty_par(LL[1]) else 1
            # The next visible leaf MUST contain a string...
            if is_valid_index(idx) and LL[idx].type == token.STRING:
                return idx

        return None

    @staticmethod
    def _assert_match(LL: List[Leaf]) -> Optional[int]:
        """
        Returns:
            string_idx such that @LL[string_idx] is equal to our target (i.e.
            matched) string, if this line matches the assert statement
            requirements listed in the 'Requirements' section of this classes'
            docstring.
                OR
            None, otherwise.
        """
        # If this line is apart of an assert statement and the first leaf
        # contains the "assert" keyword...
        if parent_type(LL[0]) == syms.assert_stmt and LL[0].value == "assert":
            is_valid_index = is_valid_index_factory(LL)

            for (i, leaf) in enumerate(LL):
                # We MUST find a comma...
                if leaf.type == token.COMMA:
                    idx = i + 2 if is_empty_par(LL[i + 1]) else i + 1

                    # That comma MUST be followed by a string...
                    if is_valid_index(idx) and LL[idx].type == token.STRING:
                        string_idx = idx

                        # Skip the string trailer, if one exists.
                        string_parser = StringParser()
                        idx = string_parser.parse(LL, string_idx)

                        # But no more leaves are allowed...
                        if not is_valid_index(idx):
                            return string_idx

        return None

    @staticmethod
    def _assign_match(LL: List[Leaf]) -> Optional[int]:
        """
        Returns:
            string_idx such that @LL[string_idx] is equal to our target (i.e.
            matched) string, if this line matches the assignment statement
            requirements listed in the 'Requirements' section of this classes'
            docstring.
                OR
            None, otherwise.
        """
        # If this line is apart of an expression statement or is a function
        # argument AND the first leaf contains a variable name...
        if (
            parent_type(LL[0]) in [syms.expr_stmt, syms.argument, syms.power]
            and LL[0].type == token.NAME
        ):
            is_valid_index = is_valid_index_factory(LL)

            for (i, leaf) in enumerate(LL):
                # We MUST find either an '=' or '+=' symbol...
                if leaf.type in [token.EQUAL, token.PLUSEQUAL]:
                    idx = i + 2 if is_empty_par(LL[i + 1]) else i + 1

                    # That symbol MUST be followed by a string...
                    if is_valid_index(idx) and LL[idx].type == token.STRING:
                        string_idx = idx

                        # Skip the string trailer, if one exists.
                        string_parser = StringParser()
                        idx = string_parser.parse(LL, string_idx)

                        # The next leaf MAY be a comma iff this line is apart
                        # of a function argument...
                        if (
                            parent_type(LL[0]) == syms.argument
                            and is_valid_index(idx)
                            and LL[idx].type == token.COMMA
                        ):
                            idx += 1

                        # But no more leaves are allowed...
                        if not is_valid_index(idx):
                            return string_idx

        return None

    @staticmethod
    def _dict_match(LL: List[Leaf]) -> Optional[int]:
        """
        Returns:
            string_idx such that @LL[string_idx] is equal to our target (i.e.
            matched) string, if this line matches the dictionary key assignment
            statement requirements listed in the 'Requirements' section of this
            classes' docstring.
                OR
            None, otherwise.
        """
        # If this line is apart of a dictionary key assignment...
        if syms.dictsetmaker in [parent_type(LL[0]), parent_type(LL[0].parent)]:
            is_valid_index = is_valid_index_factory(LL)

            for (i, leaf) in enumerate(LL):
                # We MUST find a colon...
                if leaf.type == token.COLON:
                    idx = i + 2 if is_empty_par(LL[i + 1]) else i + 1

                    # That colon MUST be followed by a string...
                    if is_valid_index(idx) and LL[idx].type == token.STRING:
                        string_idx = idx

                        # Skip the string trailer, if one exists.
                        string_parser = StringParser()
                        idx = string_parser.parse(LL, string_idx)

                        # That string MAY be followed by a comma...
                        if is_valid_index(idx) and LL[idx].type == token.COMMA:
                            idx += 1

                        # But no more leaves are allowed...
                        if not is_valid_index(idx):
                            return string_idx

        return None

    def do_transform(self, line: Line, string_idx: int) -> Iterator[TResult[Line]]:
        LL = line.leaves

        is_valid_index = is_valid_index_factory(LL)
        insert_str_child = insert_str_child_factory(LL[string_idx])

        comma_idx = -1
        ends_with_comma = False
        if LL[comma_idx].type == token.COMMA:
            ends_with_comma = True

        leaves_to_steal_comments_from = [LL[string_idx]]
        if ends_with_comma:
            leaves_to_steal_comments_from.append(LL[comma_idx])

        # --- First Line
        first_line = line.clone()
        left_leaves = LL[:string_idx]

        # We have to remember to account for (possibly invisible) LPAR and RPAR
        # leaves that already wrapped the target string. If these leaves do
        # exist, we will replace them with our own LPAR and RPAR leaves.
        old_parens_exist = False
        if left_leaves and left_leaves[-1].type == token.LPAR:
            old_parens_exist = True
            leaves_to_steal_comments_from.append(left_leaves[-1])
            left_leaves.pop()

        append_leaves(first_line, line, left_leaves)

        lpar_leaf = Leaf(token.LPAR, "(")
        if old_parens_exist:
            replace_child(LL[string_idx - 1], lpar_leaf)
        else:
            insert_str_child(lpar_leaf)
        first_line.append(lpar_leaf)

        # We throw inline comments that were originally to the right of the
        # target string to the top line. They will now be shown to the right of
        # the LPAR.
        for leaf in leaves_to_steal_comments_from:
            for comment_leaf in line.comments_after(leaf):
                first_line.append(comment_leaf, preformatted=True)

        yield Ok(first_line)

        # --- Middle (String) Line
        # We only need to yield one (possibly too long) string line, since the
        # `StringSplitter` will break it down further if necessary.
        string_value = LL[string_idx].value
        string_line = Line(
            mode=line.mode,
            depth=line.depth + 1,
            inside_brackets=True,
            should_split_rhs=line.should_split_rhs,
            magic_trailing_comma=line.magic_trailing_comma,
        )
        string_leaf = Leaf(token.STRING, string_value)
        insert_str_child(string_leaf)
        string_line.append(string_leaf)

        old_rpar_leaf = None
        if is_valid_index(string_idx + 1):
            right_leaves = LL[string_idx + 1 :]
            if ends_with_comma:
                right_leaves.pop()

            if old_parens_exist:
                assert (
                    right_leaves and right_leaves[-1].type == token.RPAR
                ), "Apparently, old parentheses do NOT exist?!"
                old_rpar_leaf = right_leaves.pop()

            append_leaves(string_line, line, right_leaves)

        yield Ok(string_line)

        # --- Last Line
        last_line = line.clone()
        last_line.bracket_tracker = first_line.bracket_tracker

        new_rpar_leaf = Leaf(token.RPAR, ")")
        if old_rpar_leaf is not None:
            replace_child(old_rpar_leaf, new_rpar_leaf)
        else:
            insert_str_child(new_rpar_leaf)
        last_line.append(new_rpar_leaf)

        # If the target string ended with a comma, we place this comma to the
        # right of the RPAR on the last line.
        if ends_with_comma:
            comma_leaf = Leaf(token.COMMA, ",")
            replace_child(LL[comma_idx], comma_leaf)
            last_line.append(comma_leaf)

        yield Ok(last_line)


class StringParser:
    """
    A state machine that aids in parsing a string's "trailer", which can be
    either non-existent, an old-style formatting sequence (e.g. `% varX` or `%
    (varX, varY)`), or a method-call / attribute access (e.g. `.format(varX,
    varY)`).

    NOTE: A new StringParser object MUST be instantiated for each string
    trailer we need to parse.

    Examples:
        We shall assume that `line` equals the `Line` object that corresponds
        to the following line of python code:
        ```
        x = "Some {}.".format("String") + some_other_string
        ```

        Furthermore, we will assume that `string_idx` is some index such that:
        ```
        assert line.leaves[string_idx].value == "Some {}."
        ```

        The following code snippet then holds:
        ```
        string_parser = StringParser()
        idx = string_parser.parse(line.leaves, string_idx)
        assert line.leaves[idx].type == token.PLUS
        ```
    """

    DEFAULT_TOKEN = -1

    # String Parser States
    START = 1
    DOT = 2
    NAME = 3
    PERCENT = 4
    SINGLE_FMT_ARG = 5
    LPAR = 6
    RPAR = 7
    DONE = 8

    # Lookup Table for Next State
    _goto: Dict[Tuple[ParserState, NodeType], ParserState] = {
        # A string trailer may start with '.' OR '%'.
        (START, token.DOT): DOT,
        (START, token.PERCENT): PERCENT,
        (START, DEFAULT_TOKEN): DONE,
        # A '.' MUST be followed by an attribute or method name.
        (DOT, token.NAME): NAME,
        # A method name MUST be followed by an '(', whereas an attribute name
        # is the last symbol in the string trailer.
        (NAME, token.LPAR): LPAR,
        (NAME, DEFAULT_TOKEN): DONE,
        # A '%' symbol can be followed by an '(' or a single argument (e.g. a
        # string or variable name).
        (PERCENT, token.LPAR): LPAR,
        (PERCENT, DEFAULT_TOKEN): SINGLE_FMT_ARG,
        # If a '%' symbol is followed by a single argument, that argument is
        # the last leaf in the string trailer.
        (SINGLE_FMT_ARG, DEFAULT_TOKEN): DONE,
        # If present, a ')' symbol is the last symbol in a string trailer.
        # (NOTE: LPARS and nested RPARS are not included in this lookup table,
        # since they are treated as a special case by the parsing logic in this
        # classes' implementation.)
        (RPAR, DEFAULT_TOKEN): DONE,
    }

    def __init__(self) -> None:
        self._state = self.START
        self._unmatched_lpars = 0

    def parse(self, leaves: List[Leaf], string_idx: int) -> int:
        """
        Pre-conditions:
            * @leaves[@string_idx].type == token.STRING

        Returns:
            The index directly after the last leaf which is apart of the string
            trailer, if a "trailer" exists.
                OR
            @string_idx + 1, if no string "trailer" exists.
        """
        assert leaves[string_idx].type == token.STRING

        idx = string_idx + 1
        while idx < len(leaves) and self._next_state(leaves[idx]):
            idx += 1
        return idx

    def _next_state(self, leaf: Leaf) -> bool:
        """
        Pre-conditions:
            * On the first call to this function, @leaf MUST be the leaf that
            was directly after the string leaf in question (e.g. if our target
            string is `line.leaves[i]` then the first call to this method must
            be `line.leaves[i + 1]`).
            * On the next call to this function, the leaf parameter passed in
            MUST be the leaf directly following @leaf.

        Returns:
            True iff @leaf is apart of the string's trailer.
        """
        # We ignore empty LPAR or RPAR leaves.
        if is_empty_par(leaf):
            return True

        next_token = leaf.type
        if next_token == token.LPAR:
            self._unmatched_lpars += 1

        current_state = self._state

        # The LPAR parser state is a special case. We will return True until we
        # find the matching RPAR token.
        if current_state == self.LPAR:
            if next_token == token.RPAR:
                self._unmatched_lpars -= 1
                if self._unmatched_lpars == 0:
                    self._state = self.RPAR
        # Otherwise, we use a lookup table to determine the next state.
        else:
            # If the lookup table matches the current state to the next
            # token, we use the lookup table.
            if (current_state, next_token) in self._goto:
                self._state = self._goto[current_state, next_token]
            else:
                # Otherwise, we check if a the current state was assigned a
                # default.
                if (current_state, self.DEFAULT_TOKEN) in self._goto:
                    self._state = self._goto[current_state, self.DEFAULT_TOKEN]
                # If no default has been assigned, then this parser has a logic
                # error.
                else:
                    raise RuntimeError(f"{self.__class__.__name__} LOGIC ERROR!")

            if self._state == self.DONE:
                return False

        return True


def TErr(err_msg: str) -> Err[CannotTransform]:
    """(T)ransform Err

    Convenience function used when working with the TResult type.
    """
    cant_transform = CannotTransform(err_msg)
    return Err(cant_transform)


def contains_pragma_comment(comment_list: List[Leaf]) -> bool:
    """
    Returns:
        True iff one of the comments in @comment_list is a pragma used by one
        of the more common static analysis tools for python (e.g. mypy, flake8,
        pylint).
    """
    for comment in comment_list:
        if comment.value.startswith(("# type:", "# noqa", "# pylint:")):
            return True

    return False


def insert_str_child_factory(string_leaf: Leaf) -> Callable[[LN], None]:
    """
    Factory for a convenience function that is used to orphan @string_leaf
    and then insert multiple new leaves into the same part of the node
    structure that @string_leaf had originally occupied.

    Examples:
        Let `string_leaf = Leaf(token.STRING, '"foo"')` and `N =
        string_leaf.parent`. Assume the node `N` has the following
        original structure:

        Node(
            expr_stmt, [
                Leaf(NAME, 'x'),
                Leaf(EQUAL, '='),
                Leaf(STRING, '"foo"'),
            ]
        )

        We then run the code snippet shown below.
        ```
        insert_str_child = insert_str_child_factory(string_leaf)

        lpar = Leaf(token.LPAR, '(')
        insert_str_child(lpar)

        bar = Leaf(token.STRING, '"bar"')
        insert_str_child(bar)

        rpar = Leaf(token.RPAR, ')')
        insert_str_child(rpar)
        ```

        After which point, it follows that `string_leaf.parent is None` and
        the node `N` now has the following structure:

        Node(
            expr_stmt, [
                Leaf(NAME, 'x'),
                Leaf(EQUAL, '='),
                Leaf(LPAR, '('),
                Leaf(STRING, '"bar"'),
                Leaf(RPAR, ')'),
            ]
        )
    """
    string_parent = string_leaf.parent
    string_child_idx = string_leaf.remove()

    def insert_str_child(child: LN) -> None:
        nonlocal string_child_idx

        assert string_parent is not None
        assert string_child_idx is not None

        string_parent.insert_child(string_child_idx, child)
        string_child_idx += 1

    return insert_str_child


def has_triple_quotes(string: str) -> bool:
    """
    Returns:
        True iff @string starts with three quotation characters.
    """
    raw_string = string.lstrip(STRING_PREFIX_CHARS)
    return raw_string[:3] in {'"""', "'''"}


def parent_type(node: Optional[LN]) -> Optional[NodeType]:
    """
    Returns:
        @node.parent.type, if @node is not None and has a parent.
            OR
        None, otherwise.
    """
    if node is None or node.parent is None:
        return None

    return node.parent.type


def is_empty_par(leaf: Leaf) -> bool:
    return is_empty_lpar(leaf) or is_empty_rpar(leaf)


def is_empty_lpar(leaf: Leaf) -> bool:
    return leaf.type == token.LPAR and leaf.value == ""


def is_empty_rpar(leaf: Leaf) -> bool:
    return leaf.type == token.RPAR and leaf.value == ""


def is_valid_index_factory(seq: Sequence[Any]) -> Callable[[int], bool]:
    """
    Examples:
        ```
        my_list = [1, 2, 3]

        is_valid_index = is_valid_index_factory(my_list)

        assert is_valid_index(0)
        assert is_valid_index(2)

        assert not is_valid_index(3)
        assert not is_valid_index(-1)
        ```
    """

    def is_valid_index(idx: int) -> bool:
        """
        Returns:
            True iff @idx is positive AND seq[@idx] does NOT raise an
            IndexError.
        """
        return 0 <= idx < len(seq)

    return is_valid_index


def line_to_string(line: Line) -> str:
    """Returns the string representation of @line.

    WARNING: This is known to be computationally expensive.
    """
    return str(line).strip("\n")


def append_leaves(
    new_line: Line, old_line: Line, leaves: List[Leaf], preformatted: bool = False
) -> None:
    """
    Append leaves (taken from @old_line) to @new_line, making sure to fix the
    underlying Node structure where appropriate.

    All of the leaves in @leaves are duplicated. The duplicates are then
    appended to @new_line and used to replace their originals in the underlying
    Node structure. Any comments attached to the old leaves are reattached to
    the new leaves.

    Pre-conditions:
        set(@leaves) is a subset of set(@old_line.leaves).
    """
    for old_leaf in leaves:
        new_leaf = Leaf(old_leaf.type, old_leaf.value)
        replace_child(old_leaf, new_leaf)
        new_line.append(new_leaf, preformatted=preformatted)

        for comment_leaf in old_line.comments_after(old_leaf):
            new_line.append(comment_leaf, preformatted=True)


def replace_child(old_child: LN, new_child: LN) -> None:
    """
    Side Effects:
        * If @old_child.parent is set, replace @old_child with @new_child in
        @old_child's underlying Node structure.
            OR
        * Otherwise, this function does nothing.
    """
    parent = old_child.parent
    if not parent:
        return

    child_idx = old_child.remove()
    if child_idx is not None:
        parent.insert_child(child_idx, new_child)


def get_string_prefix(string: str) -> str:
    """
    Pre-conditions:
        * assert_is_leaf_string(@string)

    Returns:
        @string's prefix (e.g. '', 'r', 'f', or 'rf').
    """
    assert_is_leaf_string(string)

    prefix = ""
    prefix_idx = 0
    while string[prefix_idx] in STRING_PREFIX_CHARS:
        prefix += string[prefix_idx].lower()
        prefix_idx += 1

    return prefix


def assert_is_leaf_string(string: str) -> None:
    """
    Checks the pre-condition that @string has the format that you would expect
    of `leaf.value` where `leaf` is some Leaf such that `leaf.type ==
    token.STRING`. A more precise description of the pre-conditions that are
    checked are listed below.

    Pre-conditions:
        * @string starts with either ', ", <prefix>', or <prefix>" where
        `set(<prefix>)` is some subset of `set(STRING_PREFIX_CHARS)`.
        * @string ends with a quote character (' or ").

    Raises:
        AssertionError(...) if the pre-conditions listed above are not
        satisfied.
    """
    dquote_idx = string.find('"')
    squote_idx = string.find("'")
    if -1 in [dquote_idx, squote_idx]:
        quote_idx = max(dquote_idx, squote_idx)
    else:
        quote_idx = min(squote_idx, dquote_idx)

    assert (
        0 <= quote_idx < len(string) - 1
    ), f"{string!r} is missing a starting quote character (' or \")."
    assert string[-1] in (
        "'",
        '"',
    ), f"{string!r} is missing an ending quote character (' or \")."
    assert set(string[:quote_idx]).issubset(
        set(STRING_PREFIX_CHARS)
    ), f"{set(string[:quote_idx])} is NOT a subset of {set(STRING_PREFIX_CHARS)}."


def left_hand_split(line: Line, _features: Collection[Feature] = ()) -> Iterator[Line]:
    """Split line into many lines, starting with the first matching bracket pair.

    Note: this usually looks weird, only use this for function definitions.
    Prefer RHS otherwise.  This is why this function is not symmetrical with
    :func:`right_hand_split` which also handles optional parentheses.
    """
    tail_leaves: List[Leaf] = []
    body_leaves: List[Leaf] = []
    head_leaves: List[Leaf] = []
    current_leaves = head_leaves
    matching_bracket: Optional[Leaf] = None
    for leaf in line.leaves:
        if (
            current_leaves is body_leaves
            and leaf.type in CLOSING_BRACKETS
            and leaf.opening_bracket is matching_bracket
        ):
            current_leaves = tail_leaves if body_leaves else head_leaves
        current_leaves.append(leaf)
        if current_leaves is head_leaves:
            if leaf.type in OPENING_BRACKETS:
                matching_bracket = leaf
                current_leaves = body_leaves
    if not matching_bracket:
        raise CannotSplit("No brackets found")

    head = bracket_split_build_line(head_leaves, line, matching_bracket)
    body = bracket_split_build_line(body_leaves, line, matching_bracket, is_body=True)
    tail = bracket_split_build_line(tail_leaves, line, matching_bracket)
    bracket_split_succeeded_or_raise(head, body, tail)
    for result in (head, body, tail):
        if result:
            yield result


def right_hand_split(
    line: Line,
    line_length: int,
    features: Collection[Feature] = (),
    omit: Collection[LeafID] = (),
) -> Iterator[Line]:
    """Split line into many lines, starting with the last matching bracket pair.

    If the split was by optional parentheses, attempt splitting without them, too.
    `omit` is a collection of closing bracket IDs that shouldn't be considered for
    this split.

    Note: running this function modifies `bracket_depth` on the leaves of `line`.
    """
    tail_leaves: List[Leaf] = []
    body_leaves: List[Leaf] = []
    head_leaves: List[Leaf] = []
    current_leaves = tail_leaves
    opening_bracket: Optional[Leaf] = None
    closing_bracket: Optional[Leaf] = None
    for leaf in reversed(line.leaves):
        if current_leaves is body_leaves:
            if leaf is opening_bracket:
                current_leaves = head_leaves if body_leaves else tail_leaves
        current_leaves.append(leaf)
        if current_leaves is tail_leaves:
            if leaf.type in CLOSING_BRACKETS and id(leaf) not in omit:
                opening_bracket = leaf.opening_bracket
                closing_bracket = leaf
                current_leaves = body_leaves
    if not (opening_bracket and closing_bracket and head_leaves):
        # If there is no opening or closing_bracket that means the split failed and
        # all content is in the tail.  Otherwise, if `head_leaves` are empty, it means
        # the matching `opening_bracket` wasn't available on `line` anymore.
        raise CannotSplit("No brackets found")

    tail_leaves.reverse()
    body_leaves.reverse()
    head_leaves.reverse()
    head = bracket_split_build_line(head_leaves, line, opening_bracket)
    body = bracket_split_build_line(body_leaves, line, opening_bracket, is_body=True)
    tail = bracket_split_build_line(tail_leaves, line, opening_bracket)
    bracket_split_succeeded_or_raise(head, body, tail)
    if (
        Feature.FORCE_OPTIONAL_PARENTHESES not in features
        # the opening bracket is an optional paren
        and opening_bracket.type == token.LPAR
        and not opening_bracket.value
        # the closing bracket is an optional paren
        and closing_bracket.type == token.RPAR
        and not closing_bracket.value
        # it's not an import (optional parens are the only thing we can split on
        # in this case; attempting a split without them is a waste of time)
        and not line.is_import
        # there are no standalone comments in the body
        and not body.contains_standalone_comments(0)
        # and we can actually remove the parens
        and can_omit_invisible_parens(body, line_length, omit_on_explode=omit)
    ):
        omit = {id(closing_bracket), *omit}
        try:
            yield from right_hand_split(line, line_length, features=features, omit=omit)
            return

        except CannotSplit:
            if not (
                can_be_split(body)
                or is_line_short_enough(body, line_length=line_length)
            ):
                raise CannotSplit(
                    "Splitting failed, body is still too long and can't be split."
                )

            elif head.contains_multiline_strings() or tail.contains_multiline_strings():
                raise CannotSplit(
                    "The current optional pair of parentheses is bound to fail to"
                    " satisfy the splitting algorithm because the head or the tail"
                    " contains multiline strings which by definition never fit one"
                    " line."
                )

    ensure_visible(opening_bracket)
    ensure_visible(closing_bracket)
    for result in (head, body, tail):
        if result:
            yield result


def bracket_split_succeeded_or_raise(head: Line, body: Line, tail: Line) -> None:
    """Raise :exc:`CannotSplit` if the last left- or right-hand split failed.

    Do nothing otherwise.

    A left- or right-hand split is based on a pair of brackets. Content before
    (and including) the opening bracket is left on one line, content inside the
    brackets is put on a separate line, and finally content starting with and
    following the closing bracket is put on a separate line.

    Those are called `head`, `body`, and `tail`, respectively. If the split
    produced the same line (all content in `head`) or ended up with an empty `body`
    and the `tail` is just the closing bracket, then it's considered failed.
    """
    tail_len = len(str(tail).strip())
    if not body:
        if tail_len == 0:
            raise CannotSplit("Splitting brackets produced the same line")

        elif tail_len < 3:
            raise CannotSplit(
                f"Splitting brackets on an empty body to save {tail_len} characters is"
                " not worth it"
            )


def bracket_split_build_line(
    leaves: List[Leaf], original: Line, opening_bracket: Leaf, *, is_body: bool = False
) -> Line:
    """Return a new line with given `leaves` and respective comments from `original`.

    If `is_body` is True, the result line is one-indented inside brackets and as such
    has its first leaf's prefix normalized and a trailing comma added when expected.
    """
    result = Line(mode=original.mode, depth=original.depth)
    if is_body:
        result.inside_brackets = True
        result.depth += 1
        if leaves:
            # Since body is a new indent level, remove spurious leading whitespace.
            normalize_prefix(leaves[0], inside_brackets=True)
            # Ensure a trailing comma for imports and standalone function arguments, but
            # be careful not to add one after any comments or within type annotations.
            no_commas = (
                original.is_def
                and opening_bracket.value == "("
                and not any(leaf.type == token.COMMA for leaf in leaves)
            )

            if original.is_import or no_commas:
                for i in range(len(leaves) - 1, -1, -1):
                    if leaves[i].type == STANDALONE_COMMENT:
                        continue

                    if leaves[i].type != token.COMMA:
                        new_comma = Leaf(token.COMMA, ",")
                        leaves.insert(i + 1, new_comma)
                    break

    # Populate the line
    for leaf in leaves:
        result.append(leaf, preformatted=True)
        for comment_after in original.comments_after(leaf):
            result.append(comment_after, preformatted=True)
    if is_body and should_split_line(result, opening_bracket):
        result.should_split_rhs = True
    return result


def dont_increase_indentation(split_func: Transformer) -> Transformer:
    """Normalize prefix of the first leaf in every line returned by `split_func`.

    This is a decorator over relevant split functions.
    """

    @wraps(split_func)
    def split_wrapper(line: Line, features: Collection[Feature] = ()) -> Iterator[Line]:
        for line in split_func(line, features):
            normalize_prefix(line.leaves[0], inside_brackets=True)
            yield line

    return split_wrapper


@dont_increase_indentation
def delimiter_split(line: Line, features: Collection[Feature] = ()) -> Iterator[Line]:
    """Split according to delimiters of the highest priority.

    If the appropriate Features are given, the split will add trailing commas
    also in function signatures and calls that contain `*` and `**`.
    """
    try:
        last_leaf = line.leaves[-1]
    except IndexError:
        raise CannotSplit("Line empty")

    bt = line.bracket_tracker
    try:
        delimiter_priority = bt.max_delimiter_priority(exclude={id(last_leaf)})
    except ValueError:
        raise CannotSplit("No delimiters found")

    if delimiter_priority == DOT_PRIORITY:
        if bt.delimiter_count_with_priority(delimiter_priority) == 1:
            raise CannotSplit("Splitting a single attribute from its owner looks wrong")

    current_line = Line(
        mode=line.mode, depth=line.depth, inside_brackets=line.inside_brackets
    )
    lowest_depth = sys.maxsize
    trailing_comma_safe = True

    def append_to_line(leaf: Leaf) -> Iterator[Line]:
        """Append `leaf` to current line or to new line if appending impossible."""
        nonlocal current_line
        try:
            current_line.append_safe(leaf, preformatted=True)
        except ValueError:
            yield current_line

            current_line = Line(
                mode=line.mode, depth=line.depth, inside_brackets=line.inside_brackets
            )
            current_line.append(leaf)

    for leaf in line.leaves:
        yield from append_to_line(leaf)

        for comment_after in line.comments_after(leaf):
            yield from append_to_line(comment_after)

        lowest_depth = min(lowest_depth, leaf.bracket_depth)
        if leaf.bracket_depth == lowest_depth:
            if is_vararg(leaf, within={syms.typedargslist}):
                trailing_comma_safe = (
                    trailing_comma_safe and Feature.TRAILING_COMMA_IN_DEF in features
                )
            elif is_vararg(leaf, within={syms.arglist, syms.argument}):
                trailing_comma_safe = (
                    trailing_comma_safe and Feature.TRAILING_COMMA_IN_CALL in features
                )

        leaf_priority = bt.delimiters.get(id(leaf))
        if leaf_priority == delimiter_priority:
            yield current_line

            current_line = Line(
                mode=line.mode, depth=line.depth, inside_brackets=line.inside_brackets
            )
    if current_line:
        if (
            trailing_comma_safe
            and delimiter_priority == COMMA_PRIORITY
            and current_line.leaves[-1].type != token.COMMA
            and current_line.leaves[-1].type != STANDALONE_COMMENT
        ):
            new_comma = Leaf(token.COMMA, ",")
            current_line.append(new_comma)
        yield current_line


@dont_increase_indentation
def standalone_comment_split(
    line: Line, features: Collection[Feature] = ()
) -> Iterator[Line]:
    """Split standalone comments from the rest of the line."""
    if not line.contains_standalone_comments(0):
        raise CannotSplit("Line does not have any standalone comments")

    current_line = Line(
        mode=line.mode, depth=line.depth, inside_brackets=line.inside_brackets
    )

    def append_to_line(leaf: Leaf) -> Iterator[Line]:
        """Append `leaf` to current line or to new line if appending impossible."""
        nonlocal current_line
        try:
            current_line.append_safe(leaf, preformatted=True)
        except ValueError:
            yield current_line

            current_line = Line(
                line.mode, depth=line.depth, inside_brackets=line.inside_brackets
            )
            current_line.append(leaf)

    for leaf in line.leaves:
        yield from append_to_line(leaf)

        for comment_after in line.comments_after(leaf):
            yield from append_to_line(comment_after)

    if current_line:
        yield current_line


def is_import(leaf: Leaf) -> bool:
    """Return True if the given leaf starts an import statement."""
    p = leaf.parent
    t = leaf.type
    v = leaf.value
    return bool(
        t == token.NAME
        and (
            (v == "import" and p and p.type == syms.import_name)
            or (v == "from" and p and p.type == syms.import_from)
        )
    )


def is_type_comment(leaf: Leaf, suffix: str = "") -> bool:
    """Return True if the given leaf is a special comment.
    Only returns true for type comments for now."""
    t = leaf.type
    v = leaf.value
    return t in {token.COMMENT, STANDALONE_COMMENT} and v.startswith("# type:" + suffix)


def normalize_prefix(leaf: Leaf, *, inside_brackets: bool) -> None:
    """Leave existing extra newlines if not `inside_brackets`. Remove everything
    else.

    Note: don't use backslashes for formatting or you'll lose your voting rights.
    """
    if not inside_brackets:
        spl = leaf.prefix.split("#")
        if "\\" not in spl[0]:
            nl_count = spl[-1].count("\n")
            if len(spl) > 1:
                nl_count -= 1
            leaf.prefix = "\n" * nl_count
            return

    leaf.prefix = ""


def normalize_string_prefix(leaf: Leaf, remove_u_prefix: bool = False) -> None:
    """Make all string prefixes lowercase.

    If remove_u_prefix is given, also removes any u prefix from the string.

    Note: Mutates its argument.
    """
    match = re.match(r"^([" + STRING_PREFIX_CHARS + r"]*)(.*)$", leaf.value, re.DOTALL)
    assert match is not None, f"failed to match string {leaf.value!r}"
    orig_prefix = match.group(1)
    new_prefix = orig_prefix.replace("F", "f").replace("B", "b").replace("U", "u")
    if remove_u_prefix:
        new_prefix = new_prefix.replace("u", "")
    leaf.value = f"{new_prefix}{match.group(2)}"


def normalize_string_quotes(leaf: Leaf) -> None:
    """Prefer double quotes but only if it doesn't cause more escaping.

    Adds or removes backslashes as appropriate. Doesn't parse and fix
    strings nested in f-strings (yet).

    Note: Mutates its argument.
    """
    value = leaf.value.lstrip(STRING_PREFIX_CHARS)
    if value[:3] == '"""':
        return

    elif value[:3] == "'''":
        orig_quote = "'''"
        new_quote = '"""'
    elif value[0] == '"':
        orig_quote = '"'
        new_quote = "'"
    else:
        orig_quote = "'"
        new_quote = '"'
    first_quote_pos = leaf.value.find(orig_quote)
    if first_quote_pos == -1:
        return  # There's an internal error

    prefix = leaf.value[:first_quote_pos]
    unescaped_new_quote = re.compile(rf"(([^\\]|^)(\\\\)*){new_quote}")
    escaped_new_quote = re.compile(rf"([^\\]|^)\\((?:\\\\)*){new_quote}")
    escaped_orig_quote = re.compile(rf"([^\\]|^)\\((?:\\\\)*){orig_quote}")
    body = leaf.value[first_quote_pos + len(orig_quote) : -len(orig_quote)]
    if "r" in prefix.casefold():
        if unescaped_new_quote.search(body):
            # There's at least one unescaped new_quote in this raw string
            # so converting is impossible
            return

        # Do not introduce or remove backslashes in raw strings
        new_body = body
    else:
        # remove unnecessary escapes
        new_body = sub_twice(escaped_new_quote, rf"\1\2{new_quote}", body)
        if body != new_body:
            # Consider the string without unnecessary escapes as the original
            body = new_body
            leaf.value = f"{prefix}{orig_quote}{body}{orig_quote}"
        new_body = sub_twice(escaped_orig_quote, rf"\1\2{orig_quote}", new_body)
        new_body = sub_twice(unescaped_new_quote, rf"\1\\{new_quote}", new_body)
    if "f" in prefix.casefold():
        matches = re.findall(
            r"""
            (?:[^{]|^)\{  # start of the string or a non-{ followed by a single {
                ([^{].*?)  # contents of the brackets except if begins with {{
            \}(?:[^}]|$)  # A } followed by end of the string or a non-}
            """,
            new_body,
            re.VERBOSE,
        )
        for m in matches:
            if "\\" in str(m):
                # Do not introduce backslashes in interpolated expressions
                return

    if new_quote == '"""' and new_body[-1:] == '"':
        # edge case:
        new_body = new_body[:-1] + '\\"'
    orig_escape_count = body.count("\\")
    new_escape_count = new_body.count("\\")
    if new_escape_count > orig_escape_count:
        return  # Do not introduce more escaping

    if new_escape_count == orig_escape_count and orig_quote == '"':
        return  # Prefer double quotes

    leaf.value = f"{prefix}{new_quote}{new_body}{new_quote}"


def normalize_numeric_literal(leaf: Leaf) -> None:
    """Normalizes numeric (float, int, and complex) literals.

    All letters used in the representation are normalized to lowercase (except
    in Python 2 long literals).
    """
    text = leaf.value.lower()
    if text.startswith(("0o", "0b")):
        # Leave octal and binary literals alone.
        pass
    elif text.startswith("0x"):
        text = format_hex(text)
    elif "e" in text:
        text = format_scientific_notation(text)
    elif text.endswith(("j", "l")):
        text = format_long_or_complex_number(text)
    else:
        text = format_float_or_int_string(text)
    leaf.value = text


def format_hex(text: str) -> str:
    """
    Formats a hexadecimal string like "0x12B3"
    """
    before, after = text[:2], text[2:]
    return f"{before}{after.upper()}"


def format_scientific_notation(text: str) -> str:
    """Formats a numeric string utilizing scentific notation"""
    before, after = text.split("e")
    sign = ""
    if after.startswith("-"):
        after = after[1:]
        sign = "-"
    elif after.startswith("+"):
        after = after[1:]
    before = format_float_or_int_string(before)
    return f"{before}e{sign}{after}"


def format_long_or_complex_number(text: str) -> str:
    """Formats a long or complex string like `10L` or `10j`"""
    number = text[:-1]
    suffix = text[-1]
    # Capitalize in "2L" because "l" looks too similar to "1".
    if suffix == "l":
        suffix = "L"
    return f"{format_float_or_int_string(number)}{suffix}"


def format_float_or_int_string(text: str) -> str:
    """Formats a float string like "1.0"."""
    if "." not in text:
        return text

    before, after = text.split(".")
    return f"{before or 0}.{after or 0}"


def normalize_invisible_parens(node: Node, parens_after: Set[str]) -> None:
    """Make existing optional parentheses invisible or create new ones.

    `parens_after` is a set of string leaf values immediately after which parens
    should be put.

    Standardizes on visible parentheses for single-element tuples, and keeps
    existing visible parentheses for other tuples and generator expressions.
    """
    for pc in list_comments(node.prefix, is_endmarker=False):
        if pc.value in FMT_OFF:
            # This `node` has a prefix with `# fmt: off`, don't mess with parens.
            return
    check_lpar = False
    for index, child in enumerate(list(node.children)):
        # Fixes a bug where invisible parens are not properly stripped from
        # assignment statements that contain type annotations.
        if isinstance(child, Node) and child.type == syms.annassign:
            normalize_invisible_parens(child, parens_after=parens_after)

        # Add parentheses around long tuple unpacking in assignments.
        if (
            index == 0
            and isinstance(child, Node)
            and child.type == syms.testlist_star_expr
        ):
            check_lpar = True

        if check_lpar:
            if child.type == syms.atom:
                if maybe_make_parens_invisible_in_atom(child, parent=node):
                    wrap_in_parentheses(node, child, visible=False)
            elif is_one_tuple(child):
                wrap_in_parentheses(node, child, visible=True)
            elif node.type == syms.import_from:
                # "import from" nodes store parentheses directly as part of
                # the statement
                if child.type == token.LPAR:
                    # make parentheses invisible
                    child.value = ""  # type: ignore
                    node.children[-1].value = ""  # type: ignore
                elif child.type != token.STAR:
                    # insert invisible parentheses
                    node.insert_child(index, Leaf(token.LPAR, ""))
                    node.append_child(Leaf(token.RPAR, ""))
                break

            elif not (isinstance(child, Leaf) and is_multiline_string(child)):
                wrap_in_parentheses(node, child, visible=False)

        check_lpar = isinstance(child, Leaf) and child.value in parens_after


def normalize_fmt_off(node: Node) -> None:
    """Convert content between `# fmt: off`/`# fmt: on` into standalone comments."""
    try_again = True
    while try_again:
        try_again = convert_one_fmt_off_pair(node)


def convert_one_fmt_off_pair(node: Node) -> bool:
    """Convert content of a single `# fmt: off`/`# fmt: on` into a standalone comment.

    Returns True if a pair was converted.
    """
    for leaf in node.leaves():
        previous_consumed = 0
        for comment in list_comments(leaf.prefix, is_endmarker=False):
            if comment.value not in FMT_PASS:
                previous_consumed = comment.consumed
                continue
            # We only want standalone comments. If there's no previous leaf or
            # the previous leaf is indentation, it's a standalone comment in
            # disguise.
            if comment.value in FMT_PASS and comment.type != STANDALONE_COMMENT:
                prev = preceding_leaf(leaf)
                if prev:
                    if comment.value in FMT_OFF and prev.type not in WHITESPACE:
                        continue
                    if comment.value in FMT_SKIP and prev.type in WHITESPACE:
                        continue

            ignored_nodes = list(generate_ignored_nodes(leaf, comment))
            if not ignored_nodes:
                continue

            first = ignored_nodes[0]  # Can be a container node with the `leaf`.
            parent = first.parent
            prefix = first.prefix
            first.prefix = prefix[comment.consumed :]
            hidden_value = "".join(str(n) for n in ignored_nodes)
            if comment.value in FMT_OFF:
                hidden_value = comment.value + "\n" + hidden_value
            if comment.value in FMT_SKIP:
                hidden_value += "  " + comment.value
            if hidden_value.endswith("\n"):
                # That happens when one of the `ignored_nodes` ended with a NEWLINE
                # leaf (possibly followed by a DEDENT).
                hidden_value = hidden_value[:-1]
            first_idx: Optional[int] = None
            for ignored in ignored_nodes:
                index = ignored.remove()
                if first_idx is None:
                    first_idx = index
            assert parent is not None, "INTERNAL ERROR: fmt: on/off handling (1)"
            assert first_idx is not None, "INTERNAL ERROR: fmt: on/off handling (2)"
            parent.insert_child(
                first_idx,
                Leaf(
                    STANDALONE_COMMENT,
                    hidden_value,
                    prefix=prefix[:previous_consumed] + "\n" * comment.newlines,
                ),
            )
            return True

    return False


def generate_ignored_nodes(leaf: Leaf, comment: ProtoComment) -> Iterator[LN]:
    """Starting from the container of `leaf`, generate all leaves until `# fmt: on`.

    If comment is skip, returns leaf only.
    Stops at the end of the block.
    """
    container: Optional[LN] = container_of(leaf)
    if comment.value in FMT_SKIP:
        prev_sibling = leaf.prev_sibling
        if comment.value in leaf.prefix and prev_sibling is not None:
            leaf.prefix = leaf.prefix.replace(comment.value, "")
            siblings = [prev_sibling]
            while (
                "\n" not in prev_sibling.prefix
                and prev_sibling.prev_sibling is not None
            ):
                prev_sibling = prev_sibling.prev_sibling
                siblings.insert(0, prev_sibling)
            for sibling in siblings:
                yield sibling
        elif leaf.parent is not None:
            yield leaf.parent
        return
    while container is not None and container.type != token.ENDMARKER:
        if is_fmt_on(container):
            return

        # fix for fmt: on in children
        if contains_fmt_on_at_column(container, leaf.column):
            for child in container.children:
                if contains_fmt_on_at_column(child, leaf.column):
                    return
                yield child
        else:
            yield container
            container = container.next_sibling


def is_fmt_on(container: LN) -> bool:
    """Determine whether formatting is switched on within a container.
    Determined by whether the last `# fmt:` comment is `on` or `off`.
    """
    fmt_on = False
    for comment in list_comments(container.prefix, is_endmarker=False):
        if comment.value in FMT_ON:
            fmt_on = True
        elif comment.value in FMT_OFF:
            fmt_on = False
    return fmt_on


def contains_fmt_on_at_column(container: LN, column: int) -> bool:
    """Determine if children at a given column have formatting switched on."""
    for child in container.children:
        if (
            isinstance(child, Node)
            and first_leaf_column(child) == column
            or isinstance(child, Leaf)
            and child.column == column
        ):
            if is_fmt_on(child):
                return True

    return False


def first_leaf_column(node: Node) -> Optional[int]:
    """Returns the column of the first leaf child of a node."""
    for child in node.children:
        if isinstance(child, Leaf):
            return child.column
    return None


def maybe_make_parens_invisible_in_atom(node: LN, parent: LN) -> bool:
    """If it's safe, make the parens in the atom `node` invisible, recursively.
    Additionally, remove repeated, adjacent invisible parens from the atom `node`
    as they are redundant.

    Returns whether the node should itself be wrapped in invisible parentheses.

    """

    if (
        node.type != syms.atom
        or is_empty_tuple(node)
        or is_one_tuple(node)
        or (is_yield(node) and parent.type != syms.expr_stmt)
        or max_delimiter_priority_in_atom(node) >= COMMA_PRIORITY
    ):
        return False

    if is_walrus_assignment(node):
        if parent.type in [
            syms.annassign,
            syms.expr_stmt,
            syms.assert_stmt,
            syms.return_stmt,
            # these ones aren't useful to end users, but they do please fuzzers
            syms.for_stmt,
            syms.del_stmt,
        ]:
            return False

    first = node.children[0]
    last = node.children[-1]
    if first.type == token.LPAR and last.type == token.RPAR:
        middle = node.children[1]
        # make parentheses invisible
        first.value = ""  # type: ignore
        last.value = ""  # type: ignore
        maybe_make_parens_invisible_in_atom(middle, parent=parent)

        if is_atom_with_invisible_parens(middle):
            # Strip the invisible parens from `middle` by replacing
            # it with the child in-between the invisible parens
            middle.replace(middle.children[1])

        return False

    return True


def is_atom_with_invisible_parens(node: LN) -> bool:
    """Given a `LN`, determines whether it's an atom `node` with invisible
    parens. Useful in dedupe-ing and normalizing parens.
    """
    if isinstance(node, Leaf) or node.type != syms.atom:
        return False

    first, last = node.children[0], node.children[-1]
    return (
        isinstance(first, Leaf)
        and first.type == token.LPAR
        and first.value == ""
        and isinstance(last, Leaf)
        and last.type == token.RPAR
        and last.value == ""
    )


def is_empty_tuple(node: LN) -> bool:
    """Return True if `node` holds an empty tuple."""
    return (
        node.type == syms.atom
        and len(node.children) == 2
        and node.children[0].type == token.LPAR
        and node.children[1].type == token.RPAR
    )


def unwrap_singleton_parenthesis(node: LN) -> Optional[LN]:
    """Returns `wrapped` if `node` is of the shape ( wrapped ).

    Parenthesis can be optional. Returns None otherwise"""
    if len(node.children) != 3:
        return None

    lpar, wrapped, rpar = node.children
    if not (lpar.type == token.LPAR and rpar.type == token.RPAR):
        return None

    return wrapped


def first_child_is_arith(node: Node) -> bool:
    """Whether first child is an arithmetic or a binary arithmetic expression"""
    expr_types = {
        syms.arith_expr,
        syms.shift_expr,
        syms.xor_expr,
        syms.and_expr,
    }
    return bool(node.children and node.children[0].type in expr_types)


def wrap_in_parentheses(parent: Node, child: LN, *, visible: bool = True) -> None:
    """Wrap `child` in parentheses.

    This replaces `child` with an atom holding the parentheses and the old
    child.  That requires moving the prefix.

    If `visible` is False, the leaves will be valueless (and thus invisible).
    """
    lpar = Leaf(token.LPAR, "(" if visible else "")
    rpar = Leaf(token.RPAR, ")" if visible else "")
    prefix = child.prefix
    child.prefix = ""
    index = child.remove() or 0
    new_child = Node(syms.atom, [lpar, child, rpar])
    new_child.prefix = prefix
    parent.insert_child(index, new_child)


def is_one_tuple(node: LN) -> bool:
    """Return True if `node` holds a tuple with one element, with or without parens."""
    if node.type == syms.atom:
        gexp = unwrap_singleton_parenthesis(node)
        if gexp is None or gexp.type != syms.testlist_gexp:
            return False

        return len(gexp.children) == 2 and gexp.children[1].type == token.COMMA

    return (
        node.type in IMPLICIT_TUPLE
        and len(node.children) == 2
        and node.children[1].type == token.COMMA
    )


def is_walrus_assignment(node: LN) -> bool:
    """Return True iff `node` is of the shape ( test := test )"""
    inner = unwrap_singleton_parenthesis(node)
    return inner is not None and inner.type == syms.namedexpr_test


def is_simple_decorator_trailer(node: LN, last: bool = False) -> bool:
    """Return True iff `node` is a trailer valid in a simple decorator"""
    return node.type == syms.trailer and (
        (
            len(node.children) == 2
            and node.children[0].type == token.DOT
            and node.children[1].type == token.NAME
        )
        # last trailer can be an argument-less parentheses pair
        or (
            last
            and len(node.children) == 2
            and node.children[0].type == token.LPAR
            and node.children[1].type == token.RPAR
        )
        # last trailer can be arguments
        or (
            last
            and len(node.children) == 3
            and node.children[0].type == token.LPAR
            # and node.children[1].type == syms.argument
            and node.children[2].type == token.RPAR
        )
    )


def is_simple_decorator_expression(node: LN) -> bool:
    """Return True iff `node` could be a 'dotted name' decorator

    This function takes the node of the 'namedexpr_test' of the new decorator
    grammar and test if it would be valid under the old decorator grammar.

    The old grammar was: decorator: @ dotted_name [arguments] NEWLINE
    The new grammar is : decorator: @ namedexpr_test NEWLINE
    """
    if node.type == token.NAME:
        return True
    if node.type == syms.power:
        if node.children:
            return (
                node.children[0].type == token.NAME
                and all(map(is_simple_decorator_trailer, node.children[1:-1]))
                and (
                    len(node.children) < 2
                    or is_simple_decorator_trailer(node.children[-1], last=True)
                )
            )
    return False


def is_yield(node: LN) -> bool:
    """Return True if `node` holds a `yield` or `yield from` expression."""
    if node.type == syms.yield_expr:
        return True

    if node.type == token.NAME and node.value == "yield":  # type: ignore
        return True

    if node.type != syms.atom:
        return False

    if len(node.children) != 3:
        return False

    lpar, expr, rpar = node.children
    if lpar.type == token.LPAR and rpar.type == token.RPAR:
        return is_yield(expr)

    return False


def is_vararg(leaf: Leaf, within: Set[NodeType]) -> bool:
    """Return True if `leaf` is a star or double star in a vararg or kwarg.

    If `within` includes VARARGS_PARENTS, this applies to function signatures.
    If `within` includes UNPACKING_PARENTS, it applies to right hand-side
    extended iterable unpacking (PEP 3132) and additional unpacking
    generalizations (PEP 448).
    """
    if leaf.type not in VARARGS_SPECIALS or not leaf.parent:
        return False

    p = leaf.parent
    if p.type == syms.star_expr:
        # Star expressions are also used as assignment targets in extended
        # iterable unpacking (PEP 3132).  See what its parent is instead.
        if not p.parent:
            return False

        p = p.parent

    return p.type in within


def is_multiline_string(leaf: Leaf) -> bool:
    """Return True if `leaf` is a multiline string that actually spans many lines."""
    return has_triple_quotes(leaf.value) and "\n" in leaf.value


def is_stub_suite(node: Node) -> bool:
    """Return True if `node` is a suite with a stub body."""
    if (
        len(node.children) != 4
        or node.children[0].type != token.NEWLINE
        or node.children[1].type != token.INDENT
        or node.children[3].type != token.DEDENT
    ):
        return False

    return is_stub_body(node.children[2])


def is_stub_body(node: LN) -> bool:
    """Return True if `node` is a simple statement containing an ellipsis."""
    if not isinstance(node, Node) or node.type != syms.simple_stmt:
        return False

    if len(node.children) != 2:
        return False

    child = node.children[0]
    return (
        child.type == syms.atom
        and len(child.children) == 3
        and all(leaf == Leaf(token.DOT, ".") for leaf in child.children)
    )


def max_delimiter_priority_in_atom(node: LN) -> Priority:
    """Return maximum delimiter priority inside `node`.

    This is specific to atoms with contents contained in a pair of parentheses.
    If `node` isn't an atom or there are no enclosing parentheses, returns 0.
    """
    if node.type != syms.atom:
        return 0

    first = node.children[0]
    last = node.children[-1]
    if not (first.type == token.LPAR and last.type == token.RPAR):
        return 0

    bt = BracketTracker()
    for c in node.children[1:-1]:
        if isinstance(c, Leaf):
            bt.mark(c)
        else:
            for leaf in c.leaves():
                bt.mark(leaf)
    try:
        return bt.max_delimiter_priority()

    except ValueError:
        return 0


def ensure_visible(leaf: Leaf) -> None:
    """Make sure parentheses are visible.

    They could be invisible as part of some statements (see
    :func:`normalize_invisible_parens` and :func:`visit_import_from`).
    """
    if leaf.type == token.LPAR:
        leaf.value = "("
    elif leaf.type == token.RPAR:
        leaf.value = ")"


def should_split_line(line: Line, opening_bracket: Leaf) -> bool:
    """Should `line` be immediately split with `delimiter_split()` after RHS?"""

    if not (opening_bracket.parent and opening_bracket.value in "[{("):
        return False

    # We're essentially checking if the body is delimited by commas and there's more
    # than one of them (we're excluding the trailing comma and if the delimiter priority
    # is still commas, that means there's more).
    exclude = set()
    trailing_comma = False
    try:
        last_leaf = line.leaves[-1]
        if last_leaf.type == token.COMMA:
            trailing_comma = True
            exclude.add(id(last_leaf))
        max_priority = line.bracket_tracker.max_delimiter_priority(exclude=exclude)
    except (IndexError, ValueError):
        return False

    return max_priority == COMMA_PRIORITY and (
        (line.mode.magic_trailing_comma and trailing_comma)
        # always explode imports
        or opening_bracket.parent.type in {syms.atom, syms.import_from}
    )


def is_one_tuple_between(opening: Leaf, closing: Leaf, leaves: List[Leaf]) -> bool:
    """Return True if content between `opening` and `closing` looks like a one-tuple."""
    if opening.type != token.LPAR and closing.type != token.RPAR:
        return False

    depth = closing.bracket_depth + 1
    for _opening_index, leaf in enumerate(leaves):
        if leaf is opening:
            break

    else:
        raise LookupError("Opening paren not found in `leaves`")

    commas = 0
    _opening_index += 1
    for leaf in leaves[_opening_index:]:
        if leaf is closing:
            break

        bracket_depth = leaf.bracket_depth
        if bracket_depth == depth and leaf.type == token.COMMA:
            commas += 1
            if leaf.parent and leaf.parent.type in {
                syms.arglist,
                syms.typedargslist,
            }:
                commas += 1
                break

    return commas < 2


def get_features_used(node: Node) -> Set[Feature]:
    """Return a set of (relatively) new Python features used in this file.

    Currently looking for:
    - f-strings;
    - underscores in numeric literals;
    - trailing commas after * or ** in function signatures and calls;
    - positional only arguments in function signatures and lambdas;
    - assignment expression;
    - relaxed decorator syntax;
    """
    features: Set[Feature] = set()
    for n in node.pre_order():
        if n.type == token.STRING:
            value_head = n.value[:2]  # type: ignore
            if value_head in {'f"', 'F"', "f'", "F'", "rf", "fr", "RF", "FR"}:
                features.add(Feature.F_STRINGS)

        elif n.type == token.NUMBER:
            if "_" in n.value:  # type: ignore
                features.add(Feature.NUMERIC_UNDERSCORES)

        elif n.type == token.SLASH:
            if n.parent and n.parent.type in {syms.typedargslist, syms.arglist}:
                features.add(Feature.POS_ONLY_ARGUMENTS)

        elif n.type == token.COLONEQUAL:
            features.add(Feature.ASSIGNMENT_EXPRESSIONS)

        elif n.type == syms.decorator:
            if len(n.children) > 1 and not is_simple_decorator_expression(
                n.children[1]
            ):
                features.add(Feature.RELAXED_DECORATORS)

        elif (
            n.type in {syms.typedargslist, syms.arglist}
            and n.children
            and n.children[-1].type == token.COMMA
        ):
            if n.type == syms.typedargslist:
                feature = Feature.TRAILING_COMMA_IN_DEF
            else:
                feature = Feature.TRAILING_COMMA_IN_CALL

            for ch in n.children:
                if ch.type in STARS:
                    features.add(feature)

                if ch.type == syms.argument:
                    for argch in ch.children:
                        if argch.type in STARS:
                            features.add(feature)

    return features


def detect_target_versions(node: Node) -> Set[TargetVersion]:
    """Detect the version to target based on the nodes used."""
    features = get_features_used(node)
    return {
        version for version in TargetVersion if features <= VERSION_TO_FEATURES[version]
    }


def generate_trailers_to_omit(line: Line, line_length: int) -> Iterator[Set[LeafID]]:
    """Generate sets of closing bracket IDs that should be omitted in a RHS.

    Brackets can be omitted if the entire trailer up to and including
    a preceding closing bracket fits in one line.

    Yielded sets are cumulative (contain results of previous yields, too).  First
    set is empty, unless the line should explode, in which case bracket pairs until
    the one that needs to explode are omitted.
    """

    omit: Set[LeafID] = set()
    if not line.magic_trailing_comma:
        yield omit

    length = 4 * line.depth
    opening_bracket: Optional[Leaf] = None
    closing_bracket: Optional[Leaf] = None
    inner_brackets: Set[LeafID] = set()
    for index, leaf, leaf_length in enumerate_with_length(line, reversed=True):
        length += leaf_length
        if length > line_length:
            break

        has_inline_comment = leaf_length > len(leaf.value) + len(leaf.prefix)
        if leaf.type == STANDALONE_COMMENT or has_inline_comment:
            break

        if opening_bracket:
            if leaf is opening_bracket:
                opening_bracket = None
            elif leaf.type in CLOSING_BRACKETS:
                prev = line.leaves[index - 1] if index > 0 else None
                if (
                    prev
                    and prev.type == token.COMMA
                    and not is_one_tuple_between(
                        leaf.opening_bracket, leaf, line.leaves
                    )
                ):
                    # Never omit bracket pairs with trailing commas.
                    # We need to explode on those.
                    break

                inner_brackets.add(id(leaf))
        elif leaf.type in CLOSING_BRACKETS:
            prev = line.leaves[index - 1] if index > 0 else None
            if prev and prev.type in OPENING_BRACKETS:
                # Empty brackets would fail a split so treat them as "inner"
                # brackets (e.g. only add them to the `omit` set if another
                # pair of brackets was good enough.
                inner_brackets.add(id(leaf))
                continue

            if closing_bracket:
                omit.add(id(closing_bracket))
                omit.update(inner_brackets)
                inner_brackets.clear()
                yield omit

            if (
                prev
                and prev.type == token.COMMA
                and not is_one_tuple_between(leaf.opening_bracket, leaf, line.leaves)
            ):
                # Never omit bracket pairs with trailing commas.
                # We need to explode on those.
                break

            if leaf.value:
                opening_bracket = leaf.opening_bracket
                closing_bracket = leaf


def get_future_imports(node: Node) -> Set[str]:
    """Return a set of __future__ imports in the file."""
    imports: Set[str] = set()

    def get_imports_from_children(children: List[LN]) -> Generator[str, None, None]:
        for child in children:
            if isinstance(child, Leaf):
                if child.type == token.NAME:
                    yield child.value

            elif child.type == syms.import_as_name:
                orig_name = child.children[0]
                assert isinstance(orig_name, Leaf), "Invalid syntax parsing imports"
                assert orig_name.type == token.NAME, "Invalid syntax parsing imports"
                yield orig_name.value

            elif child.type == syms.import_as_names:
                yield from get_imports_from_children(child.children)

            else:
                raise AssertionError("Invalid syntax parsing imports")

    for child in node.children:
        if child.type != syms.simple_stmt:
            break

        first_child = child.children[0]
        if isinstance(first_child, Leaf):
            # Continue looking if we see a docstring; otherwise stop.
            if (
                len(child.children) == 2
                and first_child.type == token.STRING
                and child.children[1].type == token.NEWLINE
            ):
                continue

            break

        elif first_child.type == syms.import_from:
            module_name = first_child.children[1]
            if not isinstance(module_name, Leaf) or module_name.value != "__future__":
                break

            imports |= set(get_imports_from_children(first_child.children[3:]))
        else:
            break

    return imports


@lru_cache()
def get_gitignore(root: Path) -> PathSpec:
    """Return a PathSpec matching gitignore content if present."""
    gitignore = root / ".gitignore"
    lines: List[str] = []
    if gitignore.is_file():
        with gitignore.open() as gf:
            lines = gf.readlines()
    return PathSpec.from_lines("gitwildmatch", lines)


def normalize_path_maybe_ignore(
    path: Path, root: Path, report: "Report"
) -> Optional[str]:
    """Normalize `path`. May return `None` if `path` was ignored.

    `report` is where "path ignored" output goes.
    """
    try:
        abspath = path if path.is_absolute() else Path.cwd() / path
        normalized_path = abspath.resolve().relative_to(root).as_posix()
    except OSError as e:
        report.path_ignored(path, f"cannot be read because {e}")
        return None

    except ValueError:
        if path.is_symlink():
            report.path_ignored(path, f"is a symbolic link that points outside {root}")
            return None

        raise

    return normalized_path


def path_is_excluded(
    normalized_path: str,
    pattern: Optional[Pattern[str]],
) -> bool:
    match = pattern.search(normalized_path) if pattern else None
    return bool(match and match.group(0))


def gen_python_files(
    paths: Iterable[Path],
    root: Path,
    include: Optional[Pattern[str]],
    exclude: Pattern[str],
    extend_exclude: Optional[Pattern[str]],
    force_exclude: Optional[Pattern[str]],
    report: "Report",
    gitignore: PathSpec,
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

        # First ignore files matching .gitignore
        if gitignore.match_file(normalized_path):
            report.path_ignored(child, "matches the .gitignore file content")
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
            yield from gen_python_files(
                child.iterdir(),
                root,
                include,
                exclude,
                extend_exclude,
                force_exclude,
                report,
                gitignore,
            )

        elif child.is_file():
            include_match = include.search(normalized_path) if include else True
            if include_match:
                yield child


@lru_cache()
def find_project_root(srcs: Tuple[str, ...]) -> Path:
    """Return a directory containing .git, .hg, or pyproject.toml.

    That directory will be a common parent of all files and directories
    passed in `srcs`.

    If no directory in the tree contains a marker that would specify it's the
    project root, the root of the file system is returned.
    """
    if not srcs:
        return Path("/").resolve()

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
            return directory

        if (directory / ".hg").is_dir():
            return directory

        if (directory / "pyproject.toml").is_file():
            return directory

    return directory


@lru_cache()
def find_user_pyproject_toml() -> Path:
    r"""Return the path to the top-level user configuration for black.

    This looks for ~\.black on Windows and ~/.config/black on Linux and other
    Unix systems.
    """
    if sys.platform == "win32":
        # Windows
        user_config_path = Path.home() / ".black"
    else:
        config_root = os.environ.get("XDG_CONFIG_HOME", "~/.config")
        user_config_path = Path(config_root).expanduser() / "black"
    return user_config_path.resolve()


@dataclass
class Report:
    """Provides a reformatting counter. Can be rendered with `str(report)`."""

    check: bool = False
    diff: bool = False
    quiet: bool = False
    verbose: bool = False
    change_count: int = 0
    same_count: int = 0
    failure_count: int = 0

    def done(self, src: Path, changed: Changed) -> None:
        """Increment the counter for successful reformatting. Write out a message."""
        if changed is Changed.YES:
            reformatted = "would reformat" if self.check or self.diff else "reformatted"
            if self.verbose or not self.quiet:
                out(f"{reformatted} {src}")
            self.change_count += 1
        else:
            if self.verbose:
                if changed is Changed.NO:
                    msg = f"{src} already well formatted, good job."
                else:
                    msg = f"{src} wasn't modified on disk since last run."
                out(msg, bold=False)
            self.same_count += 1

    def failed(self, src: Path, message: str) -> None:
        """Increment the counter for failed reformatting. Write out a message."""
        err(f"error: cannot format {src}: {message}")
        self.failure_count += 1

    def path_ignored(self, path: Path, message: str) -> None:
        if self.verbose:
            out(f"{path} ignored: {message}", bold=False)

    @property
    def return_code(self) -> int:
        """Return the exit code that the app should use.

        This considers the current state of changed files and failures:
        - if there were any failures, return 123;
        - if any files were changed and --check is being used, return 1;
        - otherwise return 0.
        """
        # According to http://tldp.org/LDP/abs/html/exitcodes.html starting with
        # 126 we have special return codes reserved by the shell.
        if self.failure_count:
            return 123

        elif self.change_count and self.check:
            return 1

        return 0

    def __str__(self) -> str:
        """Render a color report of the current state.

        Use `click.unstyle` to remove colors.
        """
        if self.check or self.diff:
            reformatted = "would be reformatted"
            unchanged = "would be left unchanged"
            failed = "would fail to reformat"
        else:
            reformatted = "reformatted"
            unchanged = "left unchanged"
            failed = "failed to reformat"
        report = []
        if self.change_count:
            s = "s" if self.change_count > 1 else ""
            report.append(
                click.style(f"{self.change_count} file{s} {reformatted}", bold=True)
            )
        if self.same_count:
            s = "s" if self.same_count > 1 else ""
            report.append(f"{self.same_count} file{s} {unchanged}")
        if self.failure_count:
            s = "s" if self.failure_count > 1 else ""
            report.append(
                click.style(f"{self.failure_count} file{s} {failed}", fg="red")
            )
        return ", ".join(report) + "."


def parse_ast(src: str) -> Union[ast.AST, ast3.AST, ast27.AST]:
    filename = "<unknown>"
    if sys.version_info >= (3, 8):
        # TODO: support Python 4+ ;)
        for minor_version in range(sys.version_info[1], 4, -1):
            try:
                return ast.parse(src, filename, feature_version=(3, minor_version))
            except SyntaxError:
                continue
    else:
        for feature_version in (7, 6):
            try:
                return ast3.parse(src, filename, feature_version=feature_version)
            except SyntaxError:
                continue
    if ast27.__name__ == "ast":
        raise SyntaxError(
            "The requested source code has invalid Python 3 syntax.\n"
            "If you are trying to format Python 2 files please reinstall Black"
            " with the 'python2' extra: `python3 -m pip install black[python2]`."
        )
    return ast27.parse(src)


def _fixup_ast_constants(
    node: Union[ast.AST, ast3.AST, ast27.AST]
) -> Union[ast.AST, ast3.AST, ast27.AST]:
    """Map ast nodes deprecated in 3.8 to Constant."""
    if isinstance(node, (ast.Str, ast3.Str, ast27.Str, ast.Bytes, ast3.Bytes)):
        return ast.Constant(value=node.s)

    if isinstance(node, (ast.Num, ast3.Num, ast27.Num)):
        return ast.Constant(value=node.n)

    if isinstance(node, (ast.NameConstant, ast3.NameConstant)):
        return ast.Constant(value=node.value)

    return node


def _stringify_ast(
    node: Union[ast.AST, ast3.AST, ast27.AST], depth: int = 0
) -> Iterator[str]:
    """Simple visitor generating strings to compare ASTs by content."""

    node = _fixup_ast_constants(node)

    yield f"{'  ' * depth}{node.__class__.__name__}("

    for field in sorted(node._fields):  # noqa: F402
        # TypeIgnore has only one field 'lineno' which breaks this comparison
        type_ignore_classes = (ast3.TypeIgnore, ast27.TypeIgnore)
        if sys.version_info >= (3, 8):
            type_ignore_classes += (ast.TypeIgnore,)
        if isinstance(node, type_ignore_classes):
            break

        try:
            value = getattr(node, field)
        except AttributeError:
            continue

        yield f"{'  ' * (depth+1)}{field}="

        if isinstance(value, list):
            for item in value:
                # Ignore nested tuples within del statements, because we may insert
                # parentheses and they change the AST.
                if (
                    field == "targets"
                    and isinstance(node, (ast.Delete, ast3.Delete, ast27.Delete))
                    and isinstance(item, (ast.Tuple, ast3.Tuple, ast27.Tuple))
                ):
                    for item in item.elts:
                        yield from _stringify_ast(item, depth + 2)

                elif isinstance(item, (ast.AST, ast3.AST, ast27.AST)):
                    yield from _stringify_ast(item, depth + 2)

        elif isinstance(value, (ast.AST, ast3.AST, ast27.AST)):
            yield from _stringify_ast(value, depth + 2)

        else:
            # Constant strings may be indented across newlines, if they are
            # docstrings; fold spaces after newlines when comparing. Similarly,
            # trailing and leading space may be removed.
            # Note that when formatting Python 2 code, at least with Windows
            # line-endings, docstrings can end up here as bytes instead of
            # str so make sure that we handle both cases.
            if (
                isinstance(node, ast.Constant)
                and field == "value"
                and isinstance(value, (str, bytes))
            ):
                lineend = "\n" if isinstance(value, str) else b"\n"
                # To normalize, we strip any leading and trailing space from
                # each line...
                stripped = [line.strip() for line in value.splitlines()]
                normalized = lineend.join(stripped)  # type: ignore[attr-defined]
                # ...and remove any blank lines at the beginning and end of
                # the whole string
                normalized = normalized.strip()
            else:
                normalized = value
            yield f"{'  ' * (depth+2)}{normalized!r},  # {value.__class__.__name__}"

    yield f"{'  ' * depth})  # /{node.__class__.__name__}"


def assert_equivalent(src: str, dst: str, *, pass_num: int = 1) -> None:
    """Raise AssertionError if `src` and `dst` aren't equivalent."""
    try:
        src_ast = parse_ast(src)
    except Exception as exc:
        raise AssertionError(
            "cannot use --safe with this file; failed to parse source file.  AST"
            f" error message: {exc}"
        )

    try:
        dst_ast = parse_ast(dst)
    except Exception as exc:
        log = dump_to_file("".join(traceback.format_tb(exc.__traceback__)), dst)
        raise AssertionError(
            f"INTERNAL ERROR: Black produced invalid code on pass {pass_num}: {exc}. "
            "Please report a bug on https://github.com/psf/black/issues.  "
            f"This invalid output might be helpful: {log}"
        ) from None

    src_ast_str = "\n".join(_stringify_ast(src_ast))
    dst_ast_str = "\n".join(_stringify_ast(dst_ast))
    if src_ast_str != dst_ast_str:
        log = dump_to_file(diff(src_ast_str, dst_ast_str, "src", "dst"))
        raise AssertionError(
            "INTERNAL ERROR: Black produced code that is not equivalent to the"
            f" source on pass {pass_num}.  Please report a bug on "
            f"https://github.com/psf/black/issues.  This diff might be helpful: {log}"
        ) from None


def assert_stable(src: str, dst: str, mode: Mode) -> None:
    """Raise AssertionError if `dst` reformats differently the second time."""
    newdst = format_str(dst, mode=mode)
    if dst != newdst:
        log = dump_to_file(
            str(mode),
            diff(src, dst, "source", "first pass"),
            diff(dst, newdst, "first pass", "second pass"),
        )
        raise AssertionError(
            "INTERNAL ERROR: Black produced different code on the second pass of the"
            " formatter.  Please report a bug on https://github.com/psf/black/issues."
            f"  This diff might be helpful: {log}"
        ) from None


@mypyc_attr(patchable=True)
def dump_to_file(*output: str, ensure_final_newline: bool = True) -> str:
    """Dump `output` to a temporary file. Return path to the file."""
    with tempfile.NamedTemporaryFile(
        mode="w", prefix="blk_", suffix=".log", delete=False, encoding="utf8"
    ) as f:
        for lines in output:
            f.write(lines)
            if ensure_final_newline and lines and lines[-1] != "\n":
                f.write("\n")
    return f.name


@contextmanager
def nullcontext() -> Iterator[None]:
    """Return an empty context manager.

    To be used like `nullcontext` in Python 3.7.
    """
    yield


def diff(a: str, b: str, a_name: str, b_name: str) -> str:
    """Return a unified diff string between strings `a` and `b`."""
    import difflib

    a_lines = [line for line in a.splitlines(keepends=True)]
    b_lines = [line for line in b.splitlines(keepends=True)]
    diff_lines = []
    for line in difflib.unified_diff(
        a_lines, b_lines, fromfile=a_name, tofile=b_name, n=5
    ):
        # Work around https://bugs.python.org/issue2142
        # See https://www.gnu.org/software/diffutils/manual/html_node/Incomplete-Lines.html
        if line[-1] == "\n":
            diff_lines.append(line)
        else:
            diff_lines.append(line + "\n")
            diff_lines.append("\\ No newline at end of file\n")
    return "".join(diff_lines)


def cancel(tasks: Iterable["asyncio.Task[Any]"]) -> None:
    """asyncio signal handler that cancels all `tasks` and reports to stderr."""
    err("Aborted!")
    for task in tasks:
        task.cancel()


def shutdown(loop: asyncio.AbstractEventLoop) -> None:
    """Cancel all pending tasks on `loop`, wait for them, and close the loop."""
    try:
        if sys.version_info[:2] >= (3, 7):
            all_tasks = asyncio.all_tasks
        else:
            all_tasks = asyncio.Task.all_tasks
        # This part is borrowed from asyncio/runners.py in Python 3.7b2.
        to_cancel = [task for task in all_tasks(loop) if not task.done()]
        if not to_cancel:
            return

        for task in to_cancel:
            task.cancel()
        loop.run_until_complete(
            asyncio.gather(*to_cancel, loop=loop, return_exceptions=True)
        )
    finally:
        # `concurrent.futures.Future` objects cannot be cancelled once they
        # are already running. There might be some when the `shutdown()` happened.
        # Silence their logger's spew about the event loop being closed.
        cf_logger = logging.getLogger("concurrent.futures")
        cf_logger.setLevel(logging.CRITICAL)
        loop.close()


def sub_twice(regex: Pattern[str], replacement: str, original: str) -> str:
    """Replace `regex` with `replacement` twice on `original`.

    This is used by string normalization to perform replaces on
    overlapping matches.
    """
    return regex.sub(replacement, regex.sub(replacement, original))


def re_compile_maybe_verbose(regex: str) -> Pattern[str]:
    """Compile a regular expression string in `regex`.

    If it contains newlines, use verbose mode.
    """
    if "\n" in regex:
        regex = "(?x)" + regex
    compiled: Pattern[str] = re.compile(regex)
    return compiled


def enumerate_reversed(sequence: Sequence[T]) -> Iterator[Tuple[Index, T]]:
    """Like `reversed(enumerate(sequence))` if that were possible."""
    index = len(sequence) - 1
    for element in reversed(sequence):
        yield (index, element)
        index -= 1


def enumerate_with_length(
    line: Line, reversed: bool = False
) -> Iterator[Tuple[Index, Leaf, int]]:
    """Return an enumeration of leaves with their length.

    Stops prematurely on multiline strings and standalone comments.
    """
    op = cast(
        Callable[[Sequence[Leaf]], Iterator[Tuple[Index, Leaf]]],
        enumerate_reversed if reversed else enumerate,
    )
    for index, leaf in op(line.leaves):
        length = len(leaf.prefix) + len(leaf.value)
        if "\n" in leaf.value:
            return  # Multiline strings, we can't continue.

        for comment in line.comments_after(leaf):
            length += len(comment.value)

        yield index, leaf, length


def is_line_short_enough(line: Line, *, line_length: int, line_str: str = "") -> bool:
    """Return True if `line` is no longer than `line_length`.

    Uses the provided `line_str` rendering, if any, otherwise computes a new one.
    """
    if not line_str:
        line_str = line_to_string(line)
    return (
        len(line_str) <= line_length
        and "\n" not in line_str  # multiline strings
        and not line.contains_standalone_comments()
    )


def can_be_split(line: Line) -> bool:
    """Return False if the line cannot be split *for sure*.

    This is not an exhaustive search but a cheap heuristic that we can use to
    avoid some unfortunate formattings (mostly around wrapping unsplittable code
    in unnecessary parentheses).
    """
    leaves = line.leaves
    if len(leaves) < 2:
        return False

    if leaves[0].type == token.STRING and leaves[1].type == token.DOT:
        call_count = 0
        dot_count = 0
        next = leaves[-1]
        for leaf in leaves[-2::-1]:
            if leaf.type in OPENING_BRACKETS:
                if next.type not in CLOSING_BRACKETS:
                    return False

                call_count += 1
            elif leaf.type == token.DOT:
                dot_count += 1
            elif leaf.type == token.NAME:
                if not (next.type == token.DOT or next.type in OPENING_BRACKETS):
                    return False

            elif leaf.type not in CLOSING_BRACKETS:
                return False

            if dot_count > 1 and call_count > 1:
                return False

    return True


def can_omit_invisible_parens(
    line: Line,
    line_length: int,
    omit_on_explode: Collection[LeafID] = (),
) -> bool:
    """Does `line` have a shape safe to reformat without optional parens around it?

    Returns True for only a subset of potentially nice looking formattings but
    the point is to not return false positives that end up producing lines that
    are too long.
    """
    bt = line.bracket_tracker
    if not bt.delimiters:
        # Without delimiters the optional parentheses are useless.
        return True

    max_priority = bt.max_delimiter_priority()
    if bt.delimiter_count_with_priority(max_priority) > 1:
        # With more than one delimiter of a kind the optional parentheses read better.
        return False

    if max_priority == DOT_PRIORITY:
        # A single stranded method call doesn't require optional parentheses.
        return True

    assert len(line.leaves) >= 2, "Stranded delimiter"

    # With a single delimiter, omit if the expression starts or ends with
    # a bracket.
    first = line.leaves[0]
    second = line.leaves[1]
    if first.type in OPENING_BRACKETS and second.type not in CLOSING_BRACKETS:
        if _can_omit_opening_paren(line, first=first, line_length=line_length):
            return True

        # Note: we are not returning False here because a line might have *both*
        # a leading opening bracket and a trailing closing bracket.  If the
        # opening bracket doesn't match our rule, maybe the closing will.

    penultimate = line.leaves[-2]
    last = line.leaves[-1]
    if line.magic_trailing_comma:
        try:
            penultimate, last = last_two_except(line.leaves, omit=omit_on_explode)
        except LookupError:
            # Turns out we'd omit everything.  We cannot skip the optional parentheses.
            return False

    if (
        last.type == token.RPAR
        or last.type == token.RBRACE
        or (
            # don't use indexing for omitting optional parentheses;
            # it looks weird
            last.type == token.RSQB
            and last.parent
            and last.parent.type != syms.trailer
        )
    ):
        if penultimate.type in OPENING_BRACKETS:
            # Empty brackets don't help.
            return False

        if is_multiline_string(first):
            # Additional wrapping of a multiline string in this situation is
            # unnecessary.
            return True

        if line.magic_trailing_comma and penultimate.type == token.COMMA:
            # The rightmost non-omitted bracket pair is the one we want to explode on.
            return True

        if _can_omit_closing_paren(line, last=last, line_length=line_length):
            return True

    return False


def _can_omit_opening_paren(line: Line, *, first: Leaf, line_length: int) -> bool:
    """See `can_omit_invisible_parens`."""
    remainder = False
    length = 4 * line.depth
    _index = -1
    for _index, leaf, leaf_length in enumerate_with_length(line):
        if leaf.type in CLOSING_BRACKETS and leaf.opening_bracket is first:
            remainder = True
        if remainder:
            length += leaf_length
            if length > line_length:
                break

            if leaf.type in OPENING_BRACKETS:
                # There are brackets we can further split on.
                remainder = False

    else:
        # checked the entire string and line length wasn't exceeded
        if len(line.leaves) == _index + 1:
            return True

    return False


def _can_omit_closing_paren(line: Line, *, last: Leaf, line_length: int) -> bool:
    """See `can_omit_invisible_parens`."""
    length = 4 * line.depth
    seen_other_brackets = False
    for _index, leaf, leaf_length in enumerate_with_length(line):
        length += leaf_length
        if leaf is last.opening_bracket:
            if seen_other_brackets or length <= line_length:
                return True

        elif leaf.type in OPENING_BRACKETS:
            # There are brackets we can further split on.
            seen_other_brackets = True

    return False


def last_two_except(leaves: List[Leaf], omit: Collection[LeafID]) -> Tuple[Leaf, Leaf]:
    """Return (penultimate, last) leaves skipping brackets in `omit` and contents."""
    stop_after = None
    last = None
    for leaf in reversed(leaves):
        if stop_after:
            if leaf is stop_after:
                stop_after = None
            continue

        if last:
            return leaf, last

        if id(leaf) in omit:
            stop_after = leaf.opening_bracket
        else:
            last = leaf
    else:
        raise LookupError("Last two leaves were also skipped")


def run_transformer(
    line: Line,
    transform: Transformer,
    mode: Mode,
    features: Collection[Feature],
    *,
    line_str: str = "",
) -> List[Line]:
    if not line_str:
        line_str = line_to_string(line)
    result: List[Line] = []
    for transformed_line in transform(line, features):
        if str(transformed_line).strip("\n") == line_str:
            raise CannotTransform("Line transformer returned an unchanged result")

        result.extend(transform_line(transformed_line, mode=mode, features=features))

    if not (
        transform.__name__ == "rhs"
        and line.bracket_tracker.invisible
        and not any(bracket.value for bracket in line.bracket_tracker.invisible)
        and not line.contains_multiline_strings()
        and not result[0].contains_uncollapsable_type_comments()
        and not result[0].contains_unsplittable_type_ignore()
        and not is_line_short_enough(result[0], line_length=mode.line_length)
    ):
        return result

    line_copy = line.clone()
    append_leaves(line_copy, line, line.leaves)
    features_fop = set(features) | {Feature.FORCE_OPTIONAL_PARENTHESES}
    second_opinion = run_transformer(
        line_copy, transform, mode, features_fop, line_str=line_str
    )
    if all(
        is_line_short_enough(ln, line_length=mode.line_length) for ln in second_opinion
    ):
        result = second_opinion
    return result


def get_cache_file(mode: Mode) -> Path:
    return CACHE_DIR / f"cache.{mode.get_cache_key()}.pickle"


def read_cache(mode: Mode) -> Cache:
    """Read the cache if it exists and is well formed.

    If it is not well formed, the call to write_cache later should resolve the issue.
    """
    cache_file = get_cache_file(mode)
    if not cache_file.exists():
        return {}

    with cache_file.open("rb") as fobj:
        try:
            cache: Cache = pickle.load(fobj)
        except (pickle.UnpicklingError, ValueError):
            return {}

    return cache


def get_cache_info(path: Path) -> CacheInfo:
    """Return the information used to check if a file is already formatted or not."""
    stat = path.stat()
    return stat.st_mtime, stat.st_size


def filter_cached(cache: Cache, sources: Iterable[Path]) -> Tuple[Set[Path], Set[Path]]:
    """Split an iterable of paths in `sources` into two sets.

    The first contains paths of files that modified on disk or are not in the
    cache. The other contains paths to non-modified files.
    """
    todo, done = set(), set()
    for src in sources:
        res_src = src.resolve()
        if cache.get(str(res_src)) != get_cache_info(res_src):
            todo.add(src)
        else:
            done.add(src)
    return todo, done


def write_cache(cache: Cache, sources: Iterable[Path], mode: Mode) -> None:
    """Update the cache file."""
    cache_file = get_cache_file(mode)
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        new_cache = {
            **cache,
            **{str(src.resolve()): get_cache_info(src) for src in sources},
        }
        with tempfile.NamedTemporaryFile(dir=str(cache_file.parent), delete=False) as f:
            pickle.dump(new_cache, f, protocol=4)
        os.replace(f.name, cache_file)
    except OSError:
        pass


def patch_click() -> None:
    """Make Click not crash.

    On certain misconfigured environments, Python 3 selects the ASCII encoding as the
    default which restricts paths that it can access during the lifetime of the
    application.  Click refuses to work in this scenario by raising a RuntimeError.

    In case of Black the likelihood that non-ASCII characters are going to be used in
    file paths is minimal since it's Python source code.  Moreover, this crash was
    spurious on Python 3.7 thanks to PEP 538 and PEP 540.
    """
    try:
        from click import core
        from click import _unicodefun  # type: ignore
    except ModuleNotFoundError:
        return

    for module in (core, _unicodefun):
        if hasattr(module, "_verify_python3_env"):
            module._verify_python3_env = lambda: None


def patched_main() -> None:
    freeze_support()
    patch_click()
    main()


def is_docstring(leaf: Leaf) -> bool:
    if prev_siblings_are(
        leaf.parent, [None, token.NEWLINE, token.INDENT, syms.simple_stmt]
    ):
        return True

    # Multiline docstring on the same line as the `def`.
    if prev_siblings_are(leaf.parent, [syms.parameters, token.COLON, syms.simple_stmt]):
        # `syms.parameters` is only used in funcdefs and async_funcdefs in the Python
        # grammar. We're safe to return True without further checks.
        return True

    return False


def lines_with_leading_tabs_expanded(s: str) -> List[str]:
    """
    Splits string into lines and expands only leading tabs (following the normal
    Python rules)
    """
    lines = []
    for line in s.splitlines():
        # Find the index of the first non-whitespace character after a string of
        # whitespace that includes at least one tab
        match = re.match(r"\s*\t+\s*(\S)", line)
        if match:
            first_non_whitespace_idx = match.start(1)

            lines.append(
                line[:first_non_whitespace_idx].expandtabs()
                + line[first_non_whitespace_idx:]
            )
        else:
            lines.append(line)
    return lines


def fix_docstring(docstring: str, prefix: str) -> str:
    # https://www.python.org/dev/peps/pep-0257/#handling-docstring-indentation
    if not docstring:
        return ""
    lines = lines_with_leading_tabs_expanded(docstring)
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        last_line_idx = len(lines) - 2
        for i, line in enumerate(lines[1:]):
            stripped_line = line[indent:].rstrip()
            if stripped_line or i == last_line_idx:
                trimmed.append(prefix + stripped_line)
            else:
                trimmed.append("")
    return "\n".join(trimmed)


if __name__ == "__main__":
    patched_main()
