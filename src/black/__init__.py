import io
import json
import platform
import re
import sys
import tokenize
import traceback
from collections.abc import Collection, Generator, Iterator, MutableMapping, Sequence
from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime, timezone
from enum import Enum
from json.decoder import JSONDecodeError
from pathlib import Path
from re import Pattern
from typing import Any, Optional, Union

import click
from click.core import ParameterSource
from mypy_extensions import mypyc_attr
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPatternError

from _black_version import version as __version__
from black.cache import Cache
from black.comments import normalize_fmt_off
from black.const import (
    DEFAULT_EXCLUDES,
    DEFAULT_INCLUDES,
    DEFAULT_LINE_LENGTH,
    STDIN_PLACEHOLDER,
)
from black.files import (
    best_effort_relative_path,
    find_project_root,
    find_pyproject_toml,
    find_user_pyproject_toml,
    gen_python_files,
    get_gitignore,
    parse_pyproject_toml,
    path_is_excluded,
    resolves_outside_root_or_cannot_stat,
    wrap_stream_for_windows,
)
from black.handle_ipynb_magics import (
    PYTHON_CELL_MAGICS,
    jupyter_dependencies_are_installed,
    mask_cell,
    put_trailing_semicolon_back,
    remove_trailing_semicolon,
    unmask_cell,
    validate_cell,
)
from black.linegen import LN, LineGenerator, transform_line
from black.lines import EmptyLineTracker, LinesBlock
from black.mode import (
    FUTURE_FLAG_TO_FEATURE,
    VERSION_TO_FEATURES,
    Feature,
    Mode,
    Preview,
    TargetVersion,
    supports_feature,
)
from black.nodes import STARS, is_number_token, is_simple_decorator_expression, syms
from black.output import color_diff, diff, dump_to_file, err, ipynb_diff, out
from black.parsing import (
    ASTSafetyError,
    InvalidInput,
    lib2to3_parse,
    parse_ast,
    stringify_ast,
)
from black.ranges import (
    adjusted_lines,
    convert_unchanged_lines,
    parse_line_ranges,
    sanitized_lines,
)
from black.report import Changed, NothingChanged, Report
from blib2to3.pgen2 import token
from blib2to3.pytree import Leaf, Node

COMPILED = Path(__file__).suffix in (".pyd", ".so")

FileContent = str
Encoding = str
NewLine = str

class WriteBack(Enum):
    NO, YES, DIFF, CHECK, COLOR_DIFF = range(5)

    @classmethod
    def from_configuration(cls, *, check: bool, diff: bool, color: bool = False) -> "WriteBack":
        return cls.CHECK if check and not diff else cls.COLOR_DIFF if diff and color else cls.DIFF if diff else cls.YES

FileMode = Mode

def read_pyproject_toml(ctx: click.Context, param: click.Parameter, value: Optional[str]) -> Optional[str]:
    if not value:
        value = find_pyproject_toml(ctx.params.get("src", ()), ctx.params.get("stdin_filename", None))
        if value is None:
            return None

    try:
        config = parse_pyproject_toml(value)
    except (OSError, ValueError) as e:
        raise click.FileError(filename=value, hint=f"Error reading configuration file: {e}") from None

    if not config:
        return None

    spellcheck_pyproject_toml_keys(ctx, list(config), value)
    config = {k: str(v) if not isinstance(v, (list, dict)) else v for k, v in config.items()}

    for key, expected_type in [("target_version", list), ("exclude", str), ("extend_exclude", str)]:
        if key in config and not isinstance(config[key], expected_type):
            raise click.BadOptionUsage(key.replace("_", "-"), f"Config key {key} must be a {expected_type.__name__}")

    if "line_ranges" in config:
        raise click.BadOptionUsage("line-ranges", "Cannot use line-ranges in the pyproject.toml file.")

    ctx.default_map = {**(ctx.default_map or {}), **config}
    return value

def spellcheck_pyproject_toml_keys(ctx: click.Context, config_keys: list[str], config_file_path: str) -> None:
    invalid_keys = [key for key in config_keys if key not in {param.name for param in ctx.command.params}]
    if invalid_keys:
        out(f"Invalid config keys detected: {', '.join(map(repr, invalid_keys))} (in {config_file_path})", fg="red")

def target_version_option_callback(c: click.Context, p: Union[click.Option, click.Parameter], v: tuple[str, ...]) -> list[TargetVersion]:
    return [TargetVersion[val.upper()] for val in v]

def enable_unstable_feature_callback(c: click.Context, p: Union[click.Option, click.Parameter], v: tuple[str, ...]) -> list[Preview]:
    return [Preview[val] for val in v]

def re_compile_maybe_verbose(regex: str) -> Pattern[str]:
    return re.compile(f"(?x){regex}" if "\n" in regex else regex)

def validate_regex(ctx: click.Context, param: click.Parameter, value: Optional[str]) -> Optional[Pattern[str]]:
    try:
        return re_compile_maybe_verbose(value) if value is not None else None
    except re.error as e:
        raise click.BadParameter(f"Not a valid regular expression: {e}") from None

@click.command(context_settings={"help_option_names": ["-h", "--help"]}, help="The uncompromising code formatter.")
@click.option("-c", "--code", type=str, help="Format the code passed in as a string.")
@click.option("-l", "--line-length", type=int, default=DEFAULT_LINE_LENGTH, help="How many characters per line to allow.", show_default=True)
@click.option("-t", "--target-version", type=click.Choice([v.name.lower() for v in TargetVersion]), callback=target_version_option_callback, multiple=True, help="Python versions that should be supported by Black's output.")
@click.option("--pyi", is_flag=True, help="Format all input files like typing stubs regardless of file extension.")
@click.option("--ipynb", is_flag=True, help="Format all input files like Jupyter Notebooks regardless of file extension.")
@click.option("--python-cell-magics", multiple=True, help="When processing Jupyter Notebooks, add the given magic to the list of known python-magics.", default=[])
@click.option("-x", "--skip-source-first-line", is_flag=True, help="Skip the first line of the source code.")
@click.option("-S", "--skip-string-normalization", is_flag=True, help="Don't normalize string quotes or prefixes.")
@click.option("-C", "--skip-magic-trailing-comma", is_flag=True, help="Don't use trailing commas as a reason to split lines.")
@click.option("--preview", is_flag=True, help="Enable potentially disruptive style changes that may be added to Black's main functionality in the next major release.")
@click.option("--unstable", is_flag=True, help="Enable potentially disruptive style changes that have known bugs or are not currently expected to make it into the stable style Black's next major release. Implies --preview.")
@click.option("--enable-unstable-feature", type=click.Choice([v.name for v in Preview]), callback=enable_unstable_feature_callback, multiple=True, help="Enable specific features included in the `--unstable` style. Requires `--preview`.")
@click.option("--check", is_flag=True, help="Don't write the files back, just return the status.")
@click.option("--diff", is_flag=True, help="Don't write the files back, just output a diff to indicate what changes Black would've made.")
@click.option("--color/--no-color", is_flag=True, help="Show (or do not show) colored diff. Only applies when --diff is given.")
@click.option("--line-ranges", multiple=True, metavar="START-END", help="When specified, Black will try its best to only format these lines.", default=())
@click.option("--fast/--safe", is_flag=True, help="By default, Black performs an AST safety check after formatting your code.")
@click.option("--required-version", type=str, help="Require a specific version of Black to be running.")
@click.option("--exclude", type=str, callback=validate_regex, help="A regular expression that matches files and directories that should be excluded on recursive searches.")
@click.option("--extend-exclude", type=str, callback=validate_regex, help="Like --exclude, but adds additional files and directories on top of the default values instead of overriding them.")
@click.option("--force-exclude", type=str, callback=validate_regex, help="Like --exclude, but files and directories matching this regex will be excluded even when they are passed explicitly as arguments.")
@click.option("--stdin-filename", type=str, is_eager=True, help="The name of the file when passing it through stdin.")
@click.option("--include", type=str, default=DEFAULT_INCLUDES, callback=validate_regex, help="A regular expression that matches files and directories that should be included on recursive searches.", show_default=True)
@click.option("-W", "--workers", type=click.IntRange(min=1), default=None, help="When Black formats multiple files, it may use a process pool to speed up formatting.")
@click.option("-q", "--quiet", is_flag=True, help="Stop emitting all non-critical output.")
@click.option("-v", "--verbose", is_flag=True, help="Emit messages about files that were not changed or were ignored due to exclusion patterns.")
@click.version_option(version=__version__, message=f"%(prog)s, %(version)s (compiled: {'yes' if COMPILED else 'no'})\nPython ({platform.python_implementation()}) {platform.python_version()}")
@click.argument("src", nargs=-1, type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True, allow_dash=True), is_eager=True, metavar="SRC ...")
@click.option("--config", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, allow_dash=False, path_type=str), is_eager=True, callback=read_pyproject_toml, help="Read configuration options from a configuration file.")
@click.pass_context
def main(ctx: click.Context, code: Optional[str], line_length: int, target_version: list[TargetVersion], check: bool, diff: bool, line_ranges: Sequence[str], color: bool, fast: bool, pyi: bool, ipynb: bool, python_cell_magics: Sequence[str], skip_source_first_line: bool, skip_string_normalization: bool, skip_magic_trailing_comma: bool, preview: bool, unstable: bool, enable_unstable_feature: list[Preview], quiet: bool, verbose: bool, required_version: Optional[str], include: Pattern[str], exclude: Optional[Pattern[str]], extend_exclude: Optional[Pattern[str]], force_exclude: Optional[Pattern[str]], stdin_filename: Optional[str], workers: Optional[int], src: tuple[str, ...], config: Optional[str]) -> None:
    ctx.ensure_object(dict)

    assert sys.version_info >= (3, 9), "Black requires Python 3.9+"
    if sys.version_info[:3] == (3, 12, 5):
        out("Python 3.12.5 has a memory safety issue that can cause Black's AST safety checks to fail. Please upgrade to Python 3.12.6 or downgrade to Python 3.12.4")
        ctx.exit(1)

    if src and code is not None:
        out(main.get_usage(ctx) + "\n\n'SRC' and 'code' cannot be passed simultaneously.")
        ctx.exit(1)
    if not src and code is None:
        out(main.get_usage(ctx) + "\n\nOne of 'SRC' or 'code' is required.")
        ctx.exit(1)

    if enable_unstable_feature and not (preview or unstable):
        out(main.get_usage(ctx) + "\n\n'--enable-unstable-feature' requires '--preview'.")
        ctx.exit(1)

    root, method = (find_project_root(src, stdin_filename) if code is None else (None, None))
    ctx.obj["root"] = root

    if verbose:
        if root:
            out(f"Identified `{root}` as project root containing a {method}.", fg="blue")

        if config:
            config_source = ctx.get_parameter_source("config")
            user_level_config = str(find_user_pyproject_toml())
            if config == user_level_config:
                out(f"Using configuration from user-level config at '{user_level_config}'.", fg="blue")
            elif config_source in (ParameterSource.DEFAULT, ParameterSource.DEFAULT_MAP):
                out("Using configuration from project root.", fg="blue")
            else:
                out(f"Using configuration in '{config}'.", fg="blue")
            if ctx.default_map:
                for param, value in ctx.default_map.items():
                    out(f"{param}: {value}")

    error_msg = "Oh no! 💥 💔 💥"
    if required_version and required_version != __version__ and required_version != __version__.split(".")[0]:
        err(f"{error_msg} The required version `{required_version}` does not match the running version `{__version__}`!")
        ctx.exit(1)
    if ipynb and pyi:
        err("Cannot pass both `pyi` and `ipynb` flags!")
        ctx.exit(1)

    write_back = WriteBack.from_configuration(check=check, diff=diff, color=color)
    versions = set(target_version) if target_version else set()
    mode = Mode(
        target_versions=versions,
        line_length=line_length,
        is_pyi=pyi,
        is_ipynb=ipynb,
        skip_source_first_line=skip_source_first_line,
        string_normalization=not skip_string_normalization,
        magic_trailing_comma=not skip_magic_trailing_comma,
        preview=preview,
        unstable=unstable,
        python_cell_magics=set(python_cell_magics),
        enabled_features=set(enable_unstable_feature),
    )

    lines: list[tuple[int, int]] = []
    if line_ranges:
        if ipynb:
            err("Cannot use --line-ranges with ipynb files.")
            ctx.exit(1)

        try:
            lines = parse_line_ranges(line_ranges)
        except ValueError as e:
            err(str(e))
            ctx.exit(1)

    if code is not None:
        quiet = True

    report = Report(check=check, diff=diff, quiet=quiet, verbose=verbose)

    if code is not None:
        reformat_code(content=code, fast=fast, write_back=write_back, mode=mode, report=report, lines=lines)
    else:
        assert root is not None
        try:
            sources = get_sources(root=root, src=src, quiet=quiet, verbose=verbose, include=include, exclude=exclude, extend_exclude=extend_exclude, force_exclude=force_exclude, report=report, stdin_filename=stdin_filename)
        except GitWildMatchPatternError:
            ctx.exit(1)

        path_empty(sources, "No Python files are present to be formatted. Nothing to do 😴", quiet, verbose, ctx)

        if len(sources) == 1:
            reformat_one(src=sources.pop(), fast=fast, write_back=write_back, mode=mode, report=report, lines=lines)
        else:
            from black.concurrency import reformat_many

            if lines:
                err("Cannot use --line-ranges to format multiple files.")
                ctx.exit(1)
            reformat_many(sources=sources, fast=fast, write_back=write_back, mode=mode, report=report, workers=workers)

    if verbose or not quiet:
        if code is None and (verbose or report.change_count or report.failure_count):
            out()
        out(error_msg if report.return_code else "All done! ✨ 🍰 ✨")
        if code is None:
            click.echo(str(report), err=True)
    ctx.exit(report.return_code)

def get_sources(*, root: Path, src: tuple[str, ...], quiet: bool, verbose: bool, include: Pattern[str], exclude: Optional[Pattern[str]], extend_exclude: Optional[Pattern[str]], force_exclude: Optional[Pattern[str]], report: "Report", stdin_filename: Optional[str]) -> set[Path]:
    sources: set[Path] = set()

    assert root.is_absolute(), f"INTERNAL ERROR: `root` must be absolute but is {root}"
    using_default_exclude = exclude is None
    exclude = re_compile_maybe_verbose(DEFAULT_EXCLUDES) if exclude is None else exclude
    gitignore: Optional[dict[Path, PathSpec]] = None
    root_gitignore = get_gitignore(root)

    for s in src:
        if s == "-" and stdin_filename:
            path = Path(stdin_filename)
            if path_is_excluded(stdin_filename, force_exclude):
                report.path_ignored(path, "--stdin-filename matches the --force-exclude regular expression")
                continue
            is_stdin = True
        else:
            path = Path(s)
            is_stdin = False

        if is_stdin or path.is_file():
            if resolves_outside_root_or_cannot_stat(path, root, report):
                if verbose:
                    out(f'Skipping invalid source: "{path}"', fg="red")
                continue

            root_relative_path = best_effort_relative_path(path, root).as_posix()
            root_relative_path = "/" + root_relative_path

            if path_is_excluded(root_relative_path, force_exclude):
                report.path_ignored(path, "matches the --force-exclude regular expression")
                continue

            if is_stdin:
                path = Path(f"{STDIN_PLACEHOLDER}{str(path)}")

            if path.suffix == ".ipynb" and not jupyter_dependencies_are_installed(warn=verbose or not quiet):
                continue

            if verbose:
                out(f'Found input source: "{path}"', fg="blue")
            sources.add(path)
        elif path.is_dir():
            path = root / (path.resolve().relative_to(root))
            if verbose:
                out(f'Found input source directory: "{path}"', fg="blue")

            if using_default_exclude:
                gitignore = {root: root_gitignore, path: get_gitignore(path)}
            sources.update(gen_python_files(path.iterdir(), root, include, exclude, extend_exclude, force_exclude, report, gitignore, verbose=verbose, quiet=quiet))
        elif s == "-":
            if verbose:
                out("Found input source stdin", fg="blue")
            sources.add(path)
        else:
            err(f"invalid path: {s}")

    return sources

def path_empty(src: Sized, msg: str, quiet: bool, verbose: bool, ctx: click.Context) -> None:
    if not src:
        if verbose or not quiet:
            out(msg)
        ctx.exit(0)

def reformat_code(content: str, fast: bool, write_back: WriteBack, mode: Mode, report: Report, *, lines: Collection[tuple[int, int]] = ()) -> None:
    path = Path("<string>")
    try:
        changed = Changed.NO
        if format_stdin_to_stdout(content=content, fast=fast, write_back=write_back, mode=mode, lines=lines):
            changed = Changed.YES
        report.done(path, changed)
    except Exception as exc:
        if report.verbose:
            traceback.print_exc()
        report.failed(path, str(exc))

@mypyc_attr(patchable=True)
def reformat_one(src: Path, fast: bool, write_back: WriteBack, mode: Mode, report: "Report", *, lines: Collection[tuple[int, int]] = ()) -> None:
    try:
        changed = Changed.NO

        if str(src) == "-":
            is_stdin = True
        elif str(src).startswith(STDIN_PLACEHOLDER):
            is_stdin = True
            src = Path(str(src)[len(STDIN_PLACEHOLDER):])
        else:
            is_stdin = False

        if is_stdin:
            if src.suffix == ".pyi":
                mode = replace(mode, is_pyi=True)
            elif src.suffix == ".ipynb":
                mode = replace(mode, is_ipynb=True)
            if format_stdin_to_stdout(fast=fast, write_back=write_back, mode=mode, lines=lines):
                changed = Changed.YES
        else:
            cache = Cache.read(mode)
            if write_back not in (WriteBack.DIFF, WriteBack.COLOR_DIFF):
                if not cache.is_changed(src):
                    changed = Changed.CACHED
            if changed is not Changed.CACHED and format_file_in_place(src, fast=fast, write_back=write_back, mode=mode, lines=lines):
                changed = Changed.YES
            if (write_back is WriteBack.YES and changed is not Changed.CACHED) or (write_back is WriteBack.CHECK and changed is Changed.NO):
                cache.write([src])
        report.done(src, changed)
    except Exception as exc:
        if report.verbose:
            traceback.print_exc()
        report.failed(src, str(exc))

def format_file_in_place(src: Path, fast: bool, mode: Mode, write_back: WriteBack = WriteBack.NO, lock: Any = None, *, lines: Collection[tuple[int, int]] = ()) -> bool:
    if src.suffix == ".pyi":
        mode = replace(mode, is_pyi=True)
    elif src.suffix == ".ipynb":
        mode = replace(mode, is_ipynb=True)

    then = datetime.fromtimestamp(src.stat().st_mtime, timezone.utc)
    header = b""
    with open(src, "rb") as buf:
        if mode.skip_source_first_line:
            header = buf.readline()
        src_contents, encoding, newline = decode_bytes(buf.read())
    try:
        dst_contents = format_file_contents(src_contents, fast=fast, mode=mode, lines=lines)
    except NothingChanged:
        return False
    except JSONDecodeError:
        raise ValueError(f"File '{src}' cannot be parsed as valid Jupyter notebook.") from None
    src_contents = header.decode(encoding) + src_contents
    dst_contents = header.decode(encoding) + dst_contents

    if write_back == WriteBack.YES:
        with open(src, "w", encoding=encoding, newline=newline) as f:
            f.write(dst_contents)
    elif write_back in (WriteBack.DIFF, WriteBack.COLOR_DIFF):
        now = datetime.now(timezone.utc)
        src_name = f"{src}\t{then}"
        dst_name = f"{src}\t{now}"
        if mode.is_ipynb:
            diff_contents = ipynb_diff(src_contents, dst_contents, src_name, dst_name)
        else:
            diff_contents = diff(src_contents, dst_contents, src_name, dst_name)

        if write_back == WriteBack.COLOR_DIFF:
            diff_contents = color_diff(diff_contents)

        with lock or nullcontext():
            f = io.TextIOWrapper(sys.stdout.buffer, encoding=encoding, newline=newline, write_through=True)
            f = wrap_stream_for_windows(f)
            f.write(diff_contents)
            f.detach()

    return True

def format_stdin_to_stdout(fast: bool, *, content: Optional[str] = None, write_back: WriteBack = WriteBack.NO, mode: Mode, lines: Collection[tuple[int, int]] = ()) -> bool:
    then = datetime.now(timezone.utc)

    if content is None:
        src, encoding, newline = decode_bytes(sys.stdin.buffer.read())
    else:
        src, encoding, newline = content, "utf-8", ""

    dst = src
    try:
        dst = format_file_contents(src, fast=fast, mode=mode, lines=lines)
        return True

    except NothingChanged:
        return False

    finally:
        f = io.TextIOWrapper(sys.stdout.buffer, encoding=encoding, newline=newline, write_through=True)
        if write_back == WriteBack.YES:
            if dst and dst[-1] != "\n":
                dst += "\n"
            f.write(dst)
        elif write_back in (WriteBack.DIFF, WriteBack.COLOR_DIFF):
            now = datetime.now(timezone.utc)
            src_name = f"STDIN\t{then}"
            dst_name = f"STDOUT\t{now}"
            d = diff(src, dst, src_name, dst_name)
            if write_back == WriteBack.COLOR_DIFF:
                d = color_diff(d)
                f = wrap_stream_for_windows(f)
            f.write(d)
        f.detach()

def check_stability_and_equivalence(src_contents: str, dst_contents: str, *, mode: Mode, lines: Collection[tuple[int, int]] = ()) -> None:
    assert_equivalent(src_contents, dst_contents)
    assert_stable(src_contents, dst_contents, mode=mode, lines=lines)

def format_file_contents(src_contents: str, *, fast: bool, mode: Mode, lines: Collection[tuple[int, int]] = ()) -> FileContent:
    if mode.is_ipynb:
        dst_contents = format_ipynb_string(src_contents, fast=fast, mode=mode)
    else:
        dst_contents = format_str(src_contents, mode=mode, lines=lines)
    if src_contents == dst_contents:
        raise NothingChanged

    if not fast and not mode.is_ipynb:
        check_stability_and_equivalence(src_contents, dst_contents, mode=mode, lines=lines)
    return dst_contents

def format_cell(src: str, *, fast: bool, mode: Mode) -> str:
    validate_cell(src, mode)
    src_without_trailing_semicolon, has_trailing_semicolon = remove_trailing_semicolon(src)
    try:
        masked_src, replacements = mask_cell(src_without_trailing_semicolon)
    except SyntaxError:
        raise NothingChanged from None
    masked_dst = format_str(masked_src, mode=mode)
    if not fast:
        check_stability_and_equivalence(masked_src, masked_dst, mode=mode)
    dst_without_trailing_semicolon = unmask_cell(masked_dst, replacements)
    dst = put_trailing_semicolon_back(dst_without_trailing_semicolon, has_trailing_semicolon)
    dst = dst.rstrip("\n")
    if dst == src:
        raise NothingChanged from None
    return dst

def validate_metadata(nb: MutableMapping[str, Any]) -> None:
    language = nb.get("metadata", {}).get("language_info", {}).get("name", None)
    if language is not None and language != "python":
        raise NothingChanged from None

def format_ipynb_string(src_contents: str, *, fast: bool, mode: Mode) -> FileContent:
    if not src_contents:
        raise NothingChanged

    trailing_newline = src_contents[-1] == "\n"
    modified = False
    nb = json.loads(src_contents)
    validate_metadata(nb)
    for cell in nb["cells"]:
        if cell.get("cell_type", None) == "code":
            try:
                src = "".join(cell["source"])
                dst = format_cell(src, fast=fast, mode=mode)
            except NothingChanged:
                pass
            else:
                cell["source"] = dst.splitlines(keepends=True)
                modified = True
    if modified:
        dst_contents = json.dumps(nb, indent=1, ensure_ascii=False)
        if trailing_newline:
            dst_contents = dst_contents + "\n"
        return dst_contents
    else:
        raise NothingChanged

def format_str(src_contents: str, *, mode: Mode, lines: Collection[tuple[int, int]] = ()) -> str:
    if lines:
        lines = sanitized_lines(lines, src_contents)
        if not lines:
            return src_contents
    dst_contents = _format_str_once(src_contents, mode=mode, lines=lines)
    if src_contents != dst_contents:
        if lines:
            lines = adjusted_lines(lines, src_contents, dst_contents)
        return _format_str_once(dst_contents, mode=mode, lines=lines)
    return dst_contents

def _format_str_once(src_contents: str, *, mode: Mode, lines: Collection[tuple[int, int]] = ()) -> str:
    src_node = lib2to3_parse(src_contents.lstrip(), mode.target_versions)
    dst_blocks: list[LinesBlock] = []
    if mode.target_versions:
        versions = mode.target_versions
    else:
        future_imports = get_future_imports(src_node)
        versions = detect_target_versions(src_node, future_imports=future_imports)

    context_manager_features = {feature for feature in {Feature.PARENTHESIZED_CONTEXT_MANAGERS} if supports_feature(versions, feature)}
    normalize_fmt_off(src_node, mode, lines)
    if lines:
        convert_unchanged_lines(src_node, lines)

    line_generator = LineGenerator(mode=mode, features=context_manager_features)
    elt = EmptyLineTracker(mode=mode)
    split_line_features = {feature for feature in {Feature.TRAILING_COMMA_IN_CALL, Feature.TRAILING_COMMA_IN_DEF} if supports_feature(versions, feature)}
    block: Optional[LinesBlock] = None
    for current_line in line_generator.visit(src_node):
        block = elt.maybe_empty_lines(current_line)
        dst_blocks.append(block)
        for line in transform_line(current_line, mode=mode, features=split_line_features):
            block.content_lines.append(str(line))
    if dst_blocks:
        dst_blocks[-1].after = 0
    dst_contents = []
    for block in dst_blocks:
        dst_contents.extend(block.all_lines())
    if not dst_contents:
        normalized_content, _, newline = decode_bytes(src_contents.encode("utf-8"))
        if "\n" in normalized_content:
            return newline
        return ""
    return "".join(dst_contents)

def decode_bytes(src: bytes) -> tuple[FileContent, Encoding, NewLine]:
    srcbuf = io.BytesIO(src)
    encoding, lines = tokenize.detect_encoding(srcbuf.readline)
    if not lines:
        return "", encoding, "\n"

    newline = "\r\n" if b"\r\n" == lines[0][-2:] else "\n"
    srcbuf.seek(0)
    with io.TextIOWrapper(srcbuf, encoding) as tiow:
        return tiow.read(), encoding, newline

def get_features_used(node: Node, *, future_imports: Optional[set[str]] = None) -> set[Feature]:
    features: set[Feature] = set()
    if future_imports:
        features |= {FUTURE_FLAG_TO_FEATURE[future_import] for future_import in future_imports if future_import in FUTURE_FLAG_TO_FEATURE}

    for n in node.pre_order():
        if n.type == token.FSTRING_START:
            features.add(Feature.F_STRINGS)
        elif n.type == token.RBRACE and n.parent is not None and any(child.type == token.EQUAL for child in n.parent.children):
            features.add(Feature.DEBUG_F_STRINGS)

        elif is_number_token(n):
            if "_" in n.value:
                features.add(Feature.NUMERIC_UNDERSCORES)

        elif n.type == token.SLASH:
            if n.parent and n.parent.type in {syms.typedargslist, syms.arglist, syms.varargslist}:
                features.add(Feature.POS_ONLY_ARGUMENTS)

        elif n.type == token.COLONEQUAL:
            features.add(Feature.ASSIGNMENT_EXPRESSIONS)

        elif n.type == syms.decorator:
            if len(n.children) > 1 and not is_simple_decorator_expression(n.children[1]):
                features.add(Feature.RELAXED_DECORATORS)

        elif n.type in {syms.typedargslist, syms.arglist} and n.children and n.children[-1].type == token.COMMA:
            feature = Feature.TRAILING_COMMA_IN_DEF if n.type == syms.typedargslist else Feature.TRAILING_COMMA_IN_CALL

            for ch in n.children:
                if ch.type in STARS:
                    features.add(feature)

                if ch.type == syms.argument:
                    for argch in ch.children:
                        if argch.type in STARS:
                            features.add(feature)

        elif n.type in {syms.return_stmt, syms.yield_expr} and len(n.children) >= 2 and n.children[1].type == syms.testlist_star_expr and any(child.type == syms.star_expr for child in n.children[1].children):
            features.add(Feature.UNPACKING_ON_FLOW)

        elif n.type == syms.annassign and len(n.children) >= 4 and n.children[3].type == syms.testlist_star_expr:
            features.add(Feature.ANN_ASSIGN_EXTENDED_RHS)

        elif n.type == syms.with_stmt and len(n.children) > 2 and n.children[1].type == syms.atom:
            atom_children = n.children[1].children
            if len(atom_children) == 3 and atom_children[0].type == token.LPAR and _contains_asexpr(atom_children[1]) and atom_children[2].type == token.RPAR:
                features.add(Feature.PARENTHESIZED_CONTEXT_MANAGERS)

        elif n.type == syms.match_stmt:
            features.add(Feature.PATTERN_MATCHING)

        elif n.type == syms.except_clause and len(n.children) >= 2 and n.children[1].type == token.STAR:
            features.add(Feature.EXCEPT_STAR)

        elif n.type in {syms.subscriptlist, syms.trailer} and any(child.type == syms.star_expr for child in n.children):
            features.add(Feature.VARIADIC_GENERICS)

        elif n.type == syms.tname_star and len(n.children) == 3 and n.children[2].type == syms.star_expr:
            features.add(Feature.VARIADIC_GENERICS)

        elif n.type in (syms.type_stmt, syms.typeparams):
            features.add(Feature.TYPE_PARAMS)

        elif n.type in (syms.typevartuple, syms.paramspec, syms.typevar) and n.children[-2].type == token.EQUAL:
            features.add(Feature.TYPE_PARAM_DEFAULTS)

    return features

def _contains_asexpr(node: Union[Node, Leaf]) -> bool:
    if node.type == syms.asexpr_test:
        return True
    elif node.type == syms.atom:
        if len(node.children) == 3 and node.children[0].type == token.LPAR and node.children[2].type == token.RPAR:
            return _contains_asexpr(node.children[1])
    elif node.type == syms.testlist_gexp:
        return any(_contains_asexpr(child) for child in node.children)
    return False

def detect_target_versions(node: Node, *, future_imports: Optional[set[str]] = None) -> set[TargetVersion]:
    features = get_features_used(node, future_imports=future_imports)
    return {version for version in TargetVersion if features <= VERSION_TO_FEATURES[version]}

def get_future_imports(node: Node) -> set[str]:
    imports: set[str] = set()

    def get_imports_from_children(children: list[LN]) -> Generator[str, None, None]:
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
            if len(child.children) == 2 and first_child.type == token.STRING and child.children[1].type == token.NEWLINE:
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

def _black_info() -> str:
    return f"Black {__version__} on Python ({platform.python_implementation()}) {platform.python_version()}"

def assert_equivalent(src: str, dst: str) -> None:
    try:
        src_ast = parse_ast(src)
    except Exception as exc:
        raise ASTSafetyError(f"cannot use --safe with this file; failed to parse source file AST: {exc}\nThis could be caused by running Black with an older Python version that does not support new syntax used in your source file.") from exc

    try:
        dst_ast = parse_ast(dst)
    except Exception as exc:
        log = dump_to_file("".join(traceback.format_tb(exc.__traceback__)), dst)
        raise ASTSafetyError(f"INTERNAL ERROR: {_black_info()} produced invalid code: {exc}. Please report a bug on https://github.com/psf/black/issues. This invalid output might be helpful: {log}") from None

    src_ast_str = "\n".join(stringify_ast(src_ast))
    dst_ast_str = "\n".join(stringify_ast(dst_ast))
    if src_ast_str != dst_ast_str:
        log = dump_to_file(diff(src_ast_str, dst_ast_str, "src", "dst"))
        raise ASTSafetyError(f"INTERNAL ERROR: {_black_info()} produced code that is not equivalent to the source. Please report a bug on https://github.com/psf/black/issues. This diff might be helpful: {log}") from None

def assert_stable(src: str, dst: str, mode: Mode, *, lines: Collection[tuple[int, int]] = ()) -> None:
    if lines:
        return
    newdst = _format_str_once(dst, mode=mode, lines=lines)
    if dst != newdst:
        log = dump_to_file(str(mode), diff(src, dst, "source", "first pass"), diff(dst, newdst, "first pass", "second pass"))
        raise AssertionError(f"INTERNAL ERROR: {_black_info()} produced different code on the second pass of the formatter. Please report a bug on https://github.com/psf/black/issues. This diff might be helpful: {log}") from None

@contextmanager
def nullcontext() -> Iterator[None]:
    yield

def patched_main() -> None:
    if getattr(sys, "frozen", False):
        from multiprocessing import freeze_support
        freeze_support()

    main()

if __name__ == "__main__":
    patched_main()
