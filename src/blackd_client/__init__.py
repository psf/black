"""A command-line client for blackd that only uses the standard library.

It imports nothing from black or aiohttp, so it starts faster than ``black`` and
works without the ``[d]`` extra. Several files are sent to blackd in parallel
from a small thread pool, one request per file.
"""

import argparse
import difflib
import io
import os
import re
import sys
import tokenize
import urllib.error
import urllib.request
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from enum import Enum
from typing import NamedTuple

DEFAULT_URL = "http://localhost:45484"
DEFAULT_WORKERS = 10
DEFAULT_TIMEOUT = 60.0
TARGET_VERSION_RE = re.compile(r"py3\d{1,2}")


class Changed(Enum):
    NO = 0
    YES = 1
    ERROR = 2


class Result(NamedTuple):
    src: str
    changed: Changed
    # A diff for --diff, or the bytes to write to stdout when formatting stdin.
    output: str | bytes = ""
    message: str = ""


class BlackdError(Exception):
    pass


def build_headers(args: argparse.Namespace) -> dict[str, str]:
    headers = {"X-Protocol-Version": "1"}
    if args.line_length is not None:
        headers["X-Line-Length"] = str(args.line_length)
    if args.pyi:
        headers["X-Python-Variant"] = "pyi"
    elif args.target_versions:
        headers["X-Python-Variant"] = ",".join(args.target_versions)
    if args.skip_source_first_line:
        headers["X-Skip-Source-First-Line"] = "yes"
    if args.skip_string_normalization:
        headers["X-Skip-String-Normalization"] = "yes"
    if args.skip_magic_trailing_comma:
        headers["X-Skip-Magic-Trailing-Comma"] = "yes"
    if args.preview:
        headers["X-Preview"] = "yes"
    if args.unstable:
        headers["X-Unstable"] = "yes"
    if args.enable_unstable_features:
        headers["X-Enable-Unstable-Feature"] = ",".join(args.enable_unstable_features)
    if args.fast:
        headers["X-Fast-Or-Safe"] = "fast"
    return headers


def request_format(
    url: str, src: bytes, encoding: str, headers: dict[str, str], timeout: float
) -> bytes | None:
    """Send `src` to blackd. Return the formatted bytes, or None if unchanged."""
    request = urllib.request.Request(
        url,
        data=src,
        method="POST",
        headers={**headers, "Content-Type": f"text/plain; charset={encoding}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status == 204:
                return None
            formatted: bytes = response.read()
            return formatted
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace").strip()
        if e.code == 400:
            raise BlackdError(body) from None
        raise BlackdError(f"blackd returned HTTP {e.code}: {body}") from None
    except urllib.error.URLError as e:
        raise BlackdError(f"cannot reach blackd at {url}: {e.reason}") from None
    except TimeoutError:
        raise BlackdError(f"blackd at {url} timed out after {timeout}s") from None


def diff(a: str, b: str, a_name: str, b_name: str) -> str:
    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    lines = []
    for line in difflib.unified_diff(a_lines, b_lines, a_name, b_name, n=5):
        # Like black's own --diff, end the last line even if the file doesn't.
        lines.append(line if line.endswith("\n") else line + "\n")
    return "".join(lines)


def format_one(src: str, args: argparse.Namespace, headers: dict[str, str]) -> Result:
    try:
        if src == "-":
            data = sys.stdin.buffer.read()
        elif os.path.isdir(src):
            return Result(src, Changed.ERROR, message="is a directory, pass files")
        else:
            with open(src, "rb") as f:
                data = f.read()
        encoding = tokenize.detect_encoding(io.BytesIO(data).readline)[0]
        then = datetime.now(timezone.utc)
        formatted = request_format(args.url, data, encoding, headers, args.timeout)
    except (OSError, SyntaxError, BlackdError) as e:
        return Result(src, Changed.ERROR, message=str(e))

    if formatted is None:
        return Result(src, Changed.NO, output=data if src == "-" else "")

    if args.diff:
        now = datetime.now(timezone.utc)
        output = diff(
            data.decode(encoding),
            formatted.decode(encoding),
            f"{src}\t{then}",
            f"{src}\t{now}",
        )
    elif src == "-":
        return Result(src, Changed.YES, output=formatted)
    else:
        output = ""
        if not args.check:
            try:
                with open(src, "wb") as f:
                    f.write(formatted)
            except OSError as e:
                return Result(src, Changed.ERROR, message=str(e))
    return Result(src, Changed.YES, output=output)


def plural(count: int, word: str) -> str:
    return f"{count} {word}{'' if count == 1 else 's'}"


def report(results: Sequence[Result], check: bool) -> str:
    changed = sum(r.changed is Changed.YES for r in results)
    unchanged = sum(r.changed is Changed.NO for r in results)
    failed = sum(r.changed is Changed.ERROR for r in results)
    if check:
        verbs = (
            "would be reformatted",
            "would be left unchanged",
            "would fail to reformat",
        )
    else:
        verbs = ("reformatted", "left unchanged", "failed to reformat")
    parts = []
    if changed:
        parts.append(f"{plural(changed, 'file')} {verbs[0]}")
    if unchanged:
        parts.append(f"{plural(unchanged, 'file')} {verbs[1]}")
    if failed:
        parts.append(f"{plural(failed, 'file')} {verbs[2]}")
    return ", ".join(parts) + "."


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="blackd-client",
        description=(
            "Format files with a running blackd server. Options map to blackd's"
            " request headers; unlike black, pyproject.toml is not read."
        ),
    )
    parser.add_argument("src", nargs="+", help="Files to format, or - for stdin.")
    parser.add_argument(
        "--url", default=DEFAULT_URL, help=f"blackd URL (default: {DEFAULT_URL})."
    )
    parser.add_argument(
        "-l", "--line-length", type=int, help="How many characters per line to allow."
    )
    variant = parser.add_mutually_exclusive_group()
    variant.add_argument(
        "-t",
        "--target-version",
        dest="target_versions",
        action="append",
        default=[],
        metavar="VERSION",
        help="Python version the output must support, e.g. py312. Repeatable.",
    )
    variant.add_argument(
        "--pyi", action="store_true", help="Format all input as typing stubs."
    )
    parser.add_argument(
        "--skip-source-first-line",
        action="store_true",
        help="Skip the first line of each file.",
    )
    parser.add_argument(
        "-S",
        "--skip-string-normalization",
        action="store_true",
        help="Don't normalize string quotes or prefixes.",
    )
    parser.add_argument(
        "-C",
        "--skip-magic-trailing-comma",
        action="store_true",
        help="Don't use trailing commas as a reason to split lines.",
    )
    parser.add_argument("--preview", action="store_true", help="Enable preview style.")
    parser.add_argument(
        "--unstable", action="store_true", help="Enable unstable style."
    )
    parser.add_argument(
        "--enable-unstable-feature",
        dest="enable_unstable_features",
        action="append",
        default=[],
        metavar="FEATURE",
        help="Enable one unstable feature. Repeatable.",
    )
    safety = parser.add_mutually_exclusive_group()
    safety.add_argument(
        "--fast", action="store_true", help="Skip the AST safety checks."
    )
    safety.add_argument(
        "--safe",
        dest="fast",
        action="store_false",
        help="Run the AST safety checks (default).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Don't write files back. Exit 1 if any file would change.",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Don't write files back. Print a diff for each file that would change.",
    )
    parser.add_argument(
        "-W",
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=(
            "Maximum number of requests to blackd at once (default:"
            f" {DEFAULT_WORKERS})."
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"Seconds to wait for each response (default: {DEFAULT_TIMEOUT:g}).",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Only report errors."
    )
    args = parser.parse_args(argv)
    if args.workers < 1:
        parser.error("--workers must be at least 1")
    if args.src.count("-") > 1:
        parser.error("- (stdin) can only be passed once")
    for version in args.target_versions:
        if not TARGET_VERSION_RE.fullmatch(version):
            parser.error(f"invalid target version {version!r}, expected e.g. py312")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    headers = build_headers(args)
    with ThreadPoolExecutor(max_workers=min(args.workers, len(args.src))) as pool:
        results = list(pool.map(lambda src: format_one(src, args, headers), args.src))

    for result in results:
        if result.changed is Changed.ERROR:
            print(
                f"error: cannot format {result.src}: {result.message}", file=sys.stderr
            )
            continue
        if isinstance(result.output, bytes):
            if not (args.check or args.diff):
                sys.stdout.buffer.write(result.output)
        elif result.output:
            sys.stdout.write(result.output)
        if not args.quiet and result.changed is Changed.YES and result.src != "-":
            verb = "would reformat" if args.check or args.diff else "reformatted"
            print(f"{verb} {result.src}", file=sys.stderr)

    if not args.quiet:
        print(report(results, check=args.check or args.diff), file=sys.stderr)

    if any(r.changed is Changed.ERROR for r in results):
        return 123
    if args.check and any(r.changed is Changed.YES for r in results):
        return 1
    return 0
