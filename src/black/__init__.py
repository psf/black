import asyncio
from concurrent.futures import Executor, ThreadPoolExecutor, ProcessPoolExecutor
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from functools import partial, wraps
import io
from multiprocessing import Manager, freeze_support
import os
from pathlib import Path
import regex as re
import signal
import sys
import tokenize
import traceback
from typing import (
    Any,
    Collection,
    Dict,
    Generator,
    Iterator,
    List,
    Optional,
    Pattern,
    Set,
    Sized,
    Tuple,
    TypeVar,
    Union,
)

from dataclasses import dataclass, field, replace
import click

from black.const import DEFAULT_LINE_LENGTH, DEFAULT_INCLUDES, DEFAULT_EXCLUDES
from black.const import STDIN_PLACEHOLDER
from black.nodes import WHITESPACE, STATEMENT, STANDALONE_COMMENT, STARS
from black.nodes import ASSIGNMENTS, OPENING_BRACKETS, CLOSING_BRACKETS
from black.nodes import Visitor, syms, first_child_is_arith, ensure_visible
from black.nodes import is_docstring, is_empty_tuple, is_one_tuple, is_one_tuple_between
from black.nodes import is_walrus_assignment, is_yield, is_vararg, is_multiline_string
from black.nodes import is_stub_suite, is_stub_body, is_atom_with_invisible_parens
from black.nodes import is_simple_decorator_expression, wrap_in_parentheses
from black.brackets import max_delimiter_priority_in_atom
from black.brackets import DOT_PRIORITY, COMMA_PRIORITY
from black.lines import Line, EmptyLineTracker, line_to_string, is_line_short_enough
from black.lines import can_omit_invisible_parens, can_be_split, append_leaves
from black.comments import generate_comments, list_comments, normalize_fmt_off, FMT_OFF
from black.numerics import normalize_numeric_literal
from black.strings import get_string_prefix, re_compile_maybe_verbose
from black.strings import dump_to_file, diff, color_diff, fix_docstring
from black.strings import normalize_string_prefix, normalize_string_quotes
from black.trans import Transformer, CannotTransform, StringMerger
from black.trans import StringSplitter, StringParenWrapper, StringParenStripper
from black.mode import Mode, TargetVersion
from black.mode import Feature, supports_feature, VERSION_TO_FEATURES
from black.cache import read_cache, write_cache, get_cache_info, filter_cached, Cache
from black.concurrency import cancel, shutdown
from black.output import out, err
from black.report import Report, Changed
from black.files import find_project_root, find_pyproject_toml, parse_pyproject_toml
from black.files import gen_python_files, get_gitignore, normalize_path_maybe_ignore
from black.files import wrap_stream_for_windows
from black.parsing import InvalidInput  # noqa F401
from black.parsing import lib2to3_parse, parse_ast, stringify_ast


# lib2to3 fork
from blib2to3.pytree import Node, Leaf
from blib2to3.pgen2 import token

from _black_version import version as __version__


# types
T = TypeVar("T")
FileContent = str
Encoding = str
NewLine = str
LeafID = int
LN = Union[Leaf, Node]


class NothingChanged(UserWarning):
    """Raised when reformatted code is the same as source."""


class CannotSplit(CannotTransform):
    """A readable split that fits the allotted line length is impossible."""


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


# Legacy name, left for integrations.
FileMode = Mode


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
    except (OSError, ValueError) as e:
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
    callback=validate_regex,
    help=(
        "A regular expression that matches files and directories that should be"
        " excluded on recursive searches. An empty value means no paths are excluded."
        " Use forward slashes for directories on all platforms (Windows, too)."
        " Exclusions are calculated first, inclusions later. [default:"
        f" {DEFAULT_EXCLUDES}]"
    ),
    show_default=False,
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
    exclude: Optional[Pattern],
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
    exclude: Optional[Pattern[str]],
    extend_exclude: Optional[Pattern[str]],
    force_exclude: Optional[Pattern[str]],
    report: "Report",
    stdin_filename: Optional[str],
) -> Set[Path]:
    """Compute the set of files to be formatted."""

    root = find_project_root(src)
    sources: Set[Path] = set()
    path_empty(src, "No Path provided. Nothing to do 😴", quiet, verbose, ctx)

    if exclude is None:
        exclude = re_compile_maybe_verbose(DEFAULT_EXCLUDES)
        gitignore = get_gitignore(root)
    else:
        gitignore = None

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
                node.value = normalize_string_prefix(
                    node.value, remove_u_prefix=self.remove_u_prefix
                )
                node.value = normalize_string_quotes(node.value)
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

    ll = mode.line_length
    sn = mode.string_normalization
    string_merge = StringMerger(ll, sn)
    string_paren_strip = StringParenStripper(ll, sn)
    string_split = StringSplitter(ll, sn)
    string_paren_wrap = StringParenWrapper(ll, sn)

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
    for index, leaf, leaf_length in line.enumerate_with_length(reversed=True):
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

    src_ast_str = "\n".join(stringify_ast(src_ast))
    dst_ast_str = "\n".join(stringify_ast(dst_ast))
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


@contextmanager
def nullcontext() -> Iterator[None]:
    """Return an empty context manager.

    To be used like `nullcontext` in Python 3.7.
    """
    yield


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


if __name__ == "__main__":
    patched_main()
