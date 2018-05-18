import asyncio
import pickle
from asyncio.base_events import BaseEventLoop
from concurrent.futures import Executor, ProcessPoolExecutor
from enum import Enum
from functools import partial, wraps
import keyword
import logging
from multiprocessing import Manager
import os
from pathlib import Path
import re
import tokenize
import signal
import sys
from typing import (
    Any,
    Callable,
    Collection,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Pattern,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from appdirs import user_cache_dir
from attr import dataclass, Factory
import click

# lib2to3 fork
from blib2to3.pytree import Node, Leaf, type_repr
from blib2to3 import pygram, pytree
from blib2to3.pgen2 import driver, token
from blib2to3.pgen2.parse import ParseError


__version__ = "18.5b0"
DEFAULT_LINE_LENGTH = 88

# types
syms = pygram.python_symbols
FileContent = str
Encoding = str
Depth = int
NodeType = int
LeafID = int
Priority = int
Index = int
LN = Union[Leaf, Node]
SplitFunc = Callable[["Line", bool], Iterator["Line"]]
Timestamp = float
FileSize = int
CacheInfo = Tuple[Timestamp, FileSize]
Cache = Dict[Path, CacheInfo]
out = partial(click.secho, bold=True, err=True)
err = partial(click.secho, fg="red", err=True)


class NothingChanged(UserWarning):
    """Raised by :func:`format_file` when reformatted code is the same as source."""


class CannotSplit(Exception):
    """A readable split that fits the allotted line length is impossible.

    Raised by :func:`left_hand_split`, :func:`right_hand_split`, and
    :func:`delimiter_split`.
    """


class FormatError(Exception):
    """Base exception for `# fmt: on` and `# fmt: off` handling.

    It holds the number of bytes of the prefix consumed before the format
    control comment appeared.
    """

    def __init__(self, consumed: int) -> None:
        super().__init__(consumed)
        self.consumed = consumed

    def trim_prefix(self, leaf: Leaf) -> None:
        leaf.prefix = leaf.prefix[self.consumed :]

    def leaf_from_consumed(self, leaf: Leaf) -> Leaf:
        """Returns a new Leaf from the consumed part of the prefix."""
        unformatted_prefix = leaf.prefix[: self.consumed]
        return Leaf(token.NEWLINE, unformatted_prefix)


class FormatOn(FormatError):
    """Found a comment like `# fmt: on` in the file."""


class FormatOff(FormatError):
    """Found a comment like `# fmt: off` in the file."""


class WriteBack(Enum):
    NO = 0
    YES = 1
    DIFF = 2


class Changed(Enum):
    NO = 0
    CACHED = 1
    YES = 2


@click.command()
@click.option(
    "-l",
    "--line-length",
    type=int,
    default=DEFAULT_LINE_LENGTH,
    help="How many character per line to allow.",
    show_default=True,
)
@click.option(
    "--check",
    is_flag=True,
    help=(
        "Don't write the files back, just return the status.  Return code 0 "
        "means nothing would change.  Return code 1 means some files would be "
        "reformatted.  Return code 123 means there was an internal error."
    ),
)
@click.option(
    "--diff",
    is_flag=True,
    help="Don't write the files back, just output a diff for each file on stdout.",
)
@click.option(
    "--fast/--safe",
    is_flag=True,
    help="If --fast given, skip temporary sanity checks. [default: --safe]",
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help=(
        "Don't emit non-error messages to stderr. Errors are still emitted, "
        "silence those with 2>/dev/null."
    ),
)
@click.version_option(version=__version__)
@click.argument(
    "src",
    nargs=-1,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, readable=True, allow_dash=True
    ),
)
@click.pass_context
def main(
    ctx: click.Context,
    line_length: int,
    check: bool,
    diff: bool,
    fast: bool,
    quiet: bool,
    src: List[str],
) -> None:
    """The uncompromising code formatter."""
    sources: List[Path] = []
    for s in src:
        p = Path(s)
        if p.is_dir():
            sources.extend(gen_python_files_in_dir(p))
        elif p.is_file():
            # if a file was explicitly given, we don't care about its extension
            sources.append(p)
        elif s == "-":
            sources.append(Path("-"))
        else:
            err(f"invalid path: {s}")

    if check and not diff:
        write_back = WriteBack.NO
    elif diff:
        write_back = WriteBack.DIFF
    else:
        write_back = WriteBack.YES
    report = Report(check=check, quiet=quiet)
    if len(sources) == 0:
        out("No paths given. Nothing to do 😴")
        ctx.exit(0)
        return

    elif len(sources) == 1:
        reformat_one(sources[0], line_length, fast, write_back, report)
    else:
        loop = asyncio.get_event_loop()
        executor = ProcessPoolExecutor(max_workers=os.cpu_count())
        try:
            loop.run_until_complete(
                schedule_formatting(
                    sources, line_length, fast, write_back, report, loop, executor
                )
            )
        finally:
            shutdown(loop)
        if not quiet:
            out("All done! ✨ 🍰 ✨")
            click.echo(str(report))
    ctx.exit(report.return_code)


def reformat_one(
    src: Path, line_length: int, fast: bool, write_back: WriteBack, report: "Report"
) -> None:
    """Reformat a single file under `src` without spawning child processes.

    If `quiet` is True, non-error messages are not output. `line_length`,
    `write_back`, and `fast` options are passed to :func:`format_file_in_place`.
    """
    try:
        changed = Changed.NO
        if not src.is_file() and str(src) == "-":
            if format_stdin_to_stdout(
                line_length=line_length, fast=fast, write_back=write_back
            ):
                changed = Changed.YES
        else:
            cache: Cache = {}
            if write_back != WriteBack.DIFF:
                cache = read_cache(line_length)
                src = src.resolve()
                if src in cache and cache[src] == get_cache_info(src):
                    changed = Changed.CACHED
            if changed is not Changed.CACHED and format_file_in_place(
                src, line_length=line_length, fast=fast, write_back=write_back
            ):
                changed = Changed.YES
            if write_back == WriteBack.YES and changed is not Changed.NO:
                write_cache(cache, [src], line_length)
        report.done(src, changed)
    except Exception as exc:
        report.failed(src, str(exc))


async def schedule_formatting(
    sources: List[Path],
    line_length: int,
    fast: bool,
    write_back: WriteBack,
    report: "Report",
    loop: BaseEventLoop,
    executor: Executor,
) -> None:
    """Run formatting of `sources` in parallel using the provided `executor`.

    (Use ProcessPoolExecutors for actual parallelism.)

    `line_length`, `write_back`, and `fast` options are passed to
    :func:`format_file_in_place`.
    """
    cache: Cache = {}
    if write_back != WriteBack.DIFF:
        cache = read_cache(line_length)
        sources, cached = filter_cached(cache, sources)
        for src in cached:
            report.done(src, Changed.CACHED)
    cancelled = []
    formatted = []
    if sources:
        lock = None
        if write_back == WriteBack.DIFF:
            # For diff output, we need locks to ensure we don't interleave output
            # from different processes.
            manager = Manager()
            lock = manager.Lock()
        tasks = {
            loop.run_in_executor(
                executor, format_file_in_place, src, line_length, fast, write_back, lock
            ): src
            for src in sorted(sources)
        }
        pending: Iterable[asyncio.Task] = tasks.keys()
        try:
            loop.add_signal_handler(signal.SIGINT, cancel, pending)
            loop.add_signal_handler(signal.SIGTERM, cancel, pending)
        except NotImplementedError:
            # There are no good alternatives for these on Windows
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
                    formatted.append(src)
                    report.done(src, Changed.YES if task.result() else Changed.NO)
    if cancelled:
        await asyncio.gather(*cancelled, loop=loop, return_exceptions=True)
    if write_back == WriteBack.YES and formatted:
        write_cache(cache, formatted, line_length)


def format_file_in_place(
    src: Path,
    line_length: int,
    fast: bool,
    write_back: WriteBack = WriteBack.NO,
    lock: Any = None,  # multiprocessing.Manager().Lock() is some crazy proxy
) -> bool:
    """Format file under `src` path. Return True if changed.

    If `write_back` is True, write reformatted code back to stdout.
    `line_length` and `fast` options are passed to :func:`format_file_contents`.
    """
    is_pyi = src.suffix == ".pyi"

    with tokenize.open(src) as src_buffer:
        src_contents = src_buffer.read()
    try:
        dst_contents = format_file_contents(
            src_contents, line_length=line_length, fast=fast, is_pyi=is_pyi
        )
    except NothingChanged:
        return False

    if write_back == write_back.YES:
        with open(src, "w", encoding=src_buffer.encoding) as f:
            f.write(dst_contents)
    elif write_back == write_back.DIFF:
        src_name = f"{src}  (original)"
        dst_name = f"{src}  (formatted)"
        diff_contents = diff(src_contents, dst_contents, src_name, dst_name)
        if lock:
            lock.acquire()
        try:
            sys.stdout.write(diff_contents)
        finally:
            if lock:
                lock.release()
    return True


def format_stdin_to_stdout(
    line_length: int, fast: bool, write_back: WriteBack = WriteBack.NO
) -> bool:
    """Format file on stdin. Return True if changed.

    If `write_back` is True, write reformatted code back to stdout.
    `line_length` and `fast` arguments are passed to :func:`format_file_contents`.
    """
    src = sys.stdin.read()
    dst = src
    try:
        dst = format_file_contents(src, line_length=line_length, fast=fast)
        return True

    except NothingChanged:
        return False

    finally:
        if write_back == WriteBack.YES:
            sys.stdout.write(dst)
        elif write_back == WriteBack.DIFF:
            src_name = "<stdin>  (original)"
            dst_name = "<stdin>  (formatted)"
            sys.stdout.write(diff(src, dst, src_name, dst_name))


def format_file_contents(
    src_contents: str, *, line_length: int, fast: bool, is_pyi: bool = False
) -> FileContent:
    """Reformat contents a file and return new contents.

    If `fast` is False, additionally confirm that the reformatted code is
    valid by calling :func:`assert_equivalent` and :func:`assert_stable` on it.
    `line_length` is passed to :func:`format_str`.
    """
    if src_contents.strip() == "":
        raise NothingChanged

    dst_contents = format_str(src_contents, line_length=line_length, is_pyi=is_pyi)
    if src_contents == dst_contents:
        raise NothingChanged

    if not fast:
        assert_equivalent(src_contents, dst_contents)
        assert_stable(
            src_contents, dst_contents, line_length=line_length, is_pyi=is_pyi
        )
    return dst_contents


def format_str(
    src_contents: str, line_length: int, *, is_pyi: bool = False
) -> FileContent:
    """Reformat a string and return new contents.

    `line_length` determines how many characters per line are allowed.
    """
    src_node = lib2to3_parse(src_contents)
    dst_contents = ""
    future_imports = get_future_imports(src_node)
    elt = EmptyLineTracker(is_pyi=is_pyi)
    py36 = is_python36(src_node)
    lines = LineGenerator(
        remove_u_prefix=py36 or "unicode_literals" in future_imports, is_pyi=is_pyi
    )
    empty_line = Line()
    after = 0
    for current_line in lines.visit(src_node):
        for _ in range(after):
            dst_contents += str(empty_line)
        before, after = elt.maybe_empty_lines(current_line)
        for _ in range(before):
            dst_contents += str(empty_line)
        for line in split_line(current_line, line_length=line_length, py36=py36):
            dst_contents += str(line)
    return dst_contents


GRAMMARS = [
    pygram.python_grammar_no_print_statement_no_exec_statement,
    pygram.python_grammar_no_print_statement,
    pygram.python_grammar,
]


def lib2to3_parse(src_txt: str) -> Node:
    """Given a string with source, return the lib2to3 Node."""
    grammar = pygram.python_grammar_no_print_statement
    if src_txt[-1] != "\n":
        nl = "\r\n" if "\r\n" in src_txt[:1024] else "\n"
        src_txt += nl
    for grammar in GRAMMARS:
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
            exc = ValueError(f"Cannot parse: {lineno}:{column}: {faulty_line}")
    else:
        raise exc from None

    if isinstance(result, Leaf):
        result = Node(syms.file_input, [result])
    return result


def lib2to3_unparse(node: Node) -> str:
    """Given a lib2to3 node, return its string representation."""
    code = str(node)
    return code


T = TypeVar("T")


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
            name = type_repr(node.type)
        yield from getattr(self, f"visit_{name}", self.visit_default)(node)

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
    def show(cls, code: str) -> None:
        """Pretty-print the lib2to3 AST of a given string of `code`.

        Convenience method for debugging.
        """
        v: DebugVisitor[None] = DebugVisitor()
        list(v.visit(lib2to3_parse(code)))


KEYWORDS = set(keyword.kwlist)
WHITESPACE = {token.DEDENT, token.INDENT, token.NEWLINE}
FLOW_CONTROL = {"return", "raise", "break", "continue"}
STATEMENT = {
    syms.if_stmt,
    syms.while_stmt,
    syms.for_stmt,
    syms.try_stmt,
    syms.except_clause,
    syms.with_stmt,
    syms.funcdef,
    syms.classdef,
}
STANDALONE_COMMENT = 153
LOGIC_OPERATORS = {"and", "or"}
COMPARATORS = {
    token.LESS,
    token.GREATER,
    token.EQEQUAL,
    token.NOTEQUAL,
    token.LESSEQUAL,
    token.GREATEREQUAL,
}
MATH_OPERATORS = {
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
STARS = {token.STAR, token.DOUBLESTAR}
VARARGS_PARENTS = {
    syms.arglist,
    syms.argument,  # double star in arglist
    syms.trailer,  # single argument to call
    syms.typedargslist,
    syms.varargslist,  # lambdas
}
UNPACKING_PARENTS = {
    syms.atom,  # single element of a list or set literal
    syms.dictsetmaker,
    syms.listmaker,
    syms.testlist_gexp,
}
TEST_DESCENDANTS = {
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
ASSIGNMENTS = {
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
COMPREHENSION_PRIORITY = 20
COMMA_PRIORITY = 18
TERNARY_PRIORITY = 16
LOGIC_PRIORITY = 14
STRING_PRIORITY = 12
COMPARATOR_PRIORITY = 10
MATH_PRIORITIES = {
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
DOT_PRIORITY = 1


@dataclass
class BracketTracker:
    """Keeps track of brackets on a line."""

    depth: int = 0
    bracket_match: Dict[Tuple[Depth, NodeType], Leaf] = Factory(dict)
    delimiters: Dict[LeafID, Priority] = Factory(dict)
    previous: Optional[Leaf] = None
    _for_loop_variable: int = 0
    _lambda_arguments: int = 0

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
            opening_bracket = self.bracket_match.pop((self.depth, leaf.type))
            leaf.opening_bracket = opening_bracket
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
        self.previous = leaf
        self.maybe_increment_lambda_arguments(leaf)
        self.maybe_increment_for_loop_variable(leaf)

    def any_open_brackets(self) -> bool:
        """Return True if there is an yet unmatched open bracket on the line."""
        return bool(self.bracket_match)

    def max_delimiter_priority(self, exclude: Iterable[LeafID] = ()) -> int:
        """Return the highest priority of a delimiter found on the line.

        Values are consistent with what `is_split_*_delimiter()` return.
        Raises ValueError on no delimiters.
        """
        return max(v for k, v in self.delimiters.items() if k not in exclude)

    def delimiter_count_with_priority(self, priority: int = 0) -> int:
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
            self._for_loop_variable += 1
            return True

        return False

    def maybe_decrement_after_for_loop_variable(self, leaf: Leaf) -> bool:
        """See `maybe_increment_for_loop_variable` above for explanation."""
        if self._for_loop_variable and leaf.type == token.NAME and leaf.value == "in":
            self.depth -= 1
            self._for_loop_variable -= 1
            return True

        return False

    def maybe_increment_lambda_arguments(self, leaf: Leaf) -> bool:
        """In a lambda expression, there might be more than one argument.

        To avoid splitting on the comma in this situation, increase the depth of
        tokens between `lambda` and `:`.
        """
        if leaf.type == token.NAME and leaf.value == "lambda":
            self.depth += 1
            self._lambda_arguments += 1
            return True

        return False

    def maybe_decrement_after_lambda_arguments(self, leaf: Leaf) -> bool:
        """See `maybe_increment_lambda_arguments` above for explanation."""
        if self._lambda_arguments and leaf.type == token.COLON:
            self.depth -= 1
            self._lambda_arguments -= 1
            return True

        return False

    def get_open_lsqb(self) -> Optional[Leaf]:
        """Return the most recent opening square bracket (if any)."""
        return self.bracket_match.get((self.depth - 1, token.RSQB))


@dataclass
class Line:
    """Holds leaves and comments. Can be printed with `str(line)`."""

    depth: int = 0
    leaves: List[Leaf] = Factory(list)
    comments: List[Tuple[Index, Leaf]] = Factory(list)
    bracket_tracker: BracketTracker = Factory(BracketTracker)
    inside_brackets: bool = False
    should_explode: bool = False

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
            self.maybe_remove_trailing_comma(leaf)
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
    def is_flow_control(self) -> bool:
        """Is this line a flow control statement?

        Those are `return`, `raise`, `break`, and `continue`.
        """
        return (
            bool(self)
            and self.leaves[0].type == token.NAME
            and self.leaves[0].value in FLOW_CONTROL
        )

    @property
    def is_yield(self) -> bool:
        """Is this line a yield statement?"""
        return (
            bool(self)
            and self.leaves[0].type == token.NAME
            and self.leaves[0].value == "yield"
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

    def contains_standalone_comments(self, depth_limit: int = sys.maxsize) -> bool:
        """If so, needs to be split before emitting."""
        for leaf in self.leaves:
            if leaf.type == STANDALONE_COMMENT:
                if leaf.bracket_depth <= depth_limit:
                    return True

        return False

    def maybe_remove_trailing_comma(self, closing: Leaf) -> bool:
        """Remove trailing comma if there is one and it's safe."""
        if not (
            self.leaves
            and self.leaves[-1].type == token.COMMA
            and closing.type in CLOSING_BRACKETS
        ):
            return False

        if closing.type == token.RBRACE:
            self.remove_trailing_comma()
            return True

        if closing.type == token.RSQB:
            comma = self.leaves[-1]
            if comma.parent and comma.parent.type == syms.listmaker:
                self.remove_trailing_comma()
                return True

        # For parens let's check if it's safe to remove the comma.
        # Imports are always safe.
        if self.is_import:
            self.remove_trailing_comma()
            return True

        # Otheriwsse, if the trailing one is the only one, we might mistakenly
        # change a tuple into a different type by removing the comma.
        depth = closing.bracket_depth + 1
        commas = 0
        opening = closing.opening_bracket
        for _opening_index, leaf in enumerate(self.leaves):
            if leaf is opening:
                break

        else:
            return False

        for leaf in self.leaves[_opening_index + 1 :]:
            if leaf is closing:
                break

            bracket_depth = leaf.bracket_depth
            if bracket_depth == depth and leaf.type == token.COMMA:
                commas += 1
                if leaf.parent and leaf.parent.type == syms.arglist:
                    commas += 1
                    break

        if commas > 1:
            self.remove_trailing_comma()
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

        after = len(self.leaves) - 1
        if after == -1:
            comment.type = STANDALONE_COMMENT
            comment.prefix = ""
            return False

        else:
            self.comments.append((after, comment))
            return True

    def comments_after(self, leaf: Leaf, _index: int = -1) -> Iterator[Leaf]:
        """Generate comments that should appear directly after `leaf`.

        Provide a non-negative leaf `_index` to speed up the function.
        """
        if _index == -1:
            for _index, _leaf in enumerate(self.leaves):
                if leaf is _leaf:
                    break

            else:
                return

        for index, comment_after in self.comments:
            if _index == index:
                yield comment_after

    def remove_trailing_comma(self) -> None:
        """Remove the trailing comma and moves the comments attached to it."""
        comma_index = len(self.leaves) - 1
        for i in range(len(self.comments)):
            comment_index, comment = self.comments[i]
            if comment_index == comma_index:
                self.comments[i] = (comma_index - 1, comment)
        self.leaves.pop()

    def is_complex_subscript(self, leaf: Leaf) -> bool:
        """Return True iff `leaf` is part of a slice with non-trivial exprs."""
        open_lsqb = (
            leaf if leaf.type == token.LSQB else self.bracket_tracker.get_open_lsqb()
        )
        if open_lsqb is None:
            return False

        subscript_start = open_lsqb.next_sibling
        if (
            isinstance(subscript_start, Node)
            and subscript_start.type == syms.subscriptlist
        ):
            subscript_start = child_towards(subscript_start, leaf)
        return subscript_start is not None and any(
            n.type in TEST_DESCENDANTS for n in subscript_start.pre_order()
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
        for _, comment in self.comments:
            res += str(comment)
        return res + "\n"

    def __bool__(self) -> bool:
        """Return True if the line has leaves or comments."""
        return bool(self.leaves or self.comments)


class UnformattedLines(Line):
    """Just like :class:`Line` but stores lines which aren't reformatted."""

    def append(self, leaf: Leaf, preformatted: bool = True) -> None:
        """Just add a new `leaf` to the end of the lines.

        The `preformatted` argument is ignored.

        Keeps track of indentation `depth`, which is useful when the user
        says `# fmt: on`. Otherwise, doesn't do anything with the `leaf`.
        """
        try:
            list(generate_comments(leaf))
        except FormatOn as f_on:
            self.leaves.append(f_on.leaf_from_consumed(leaf))
            raise

        self.leaves.append(leaf)
        if leaf.type == token.INDENT:
            self.depth += 1
        elif leaf.type == token.DEDENT:
            self.depth -= 1

    def __str__(self) -> str:
        """Render unformatted lines from leaves which were added with `append()`.

        `depth` is not used for indentation in this case.
        """
        if not self:
            return "\n"

        res = ""
        for leaf in self.leaves:
            res += str(leaf)
        return res

    def append_comment(self, comment: Leaf) -> bool:
        """Not implemented in this class. Raises `NotImplementedError`."""
        raise NotImplementedError("Unformatted lines don't store comments separately.")

    def maybe_remove_trailing_comma(self, closing: Leaf) -> bool:
        """Does nothing and returns False."""
        return False

    def maybe_increment_for_loop_variable(self, leaf: Leaf) -> bool:
        """Does nothing and returns False."""
        return False


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
    previous_defs: List[int] = Factory(list)

    def maybe_empty_lines(self, current_line: Line) -> Tuple[int, int]:
        """Return the number of extra empty lines before and after the `current_line`.

        This is for separating `def`, `async def` and `class` with extra empty
        lines (two on module-level), as well as providing an extra empty line
        after flow control keywords to make them more prominent.
        """
        if isinstance(current_line, UnformattedLines):
            return 0, 0

        before, after = self._maybe_empty_lines(current_line)
        before -= self.previous_after
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
        is_decorator = current_line.is_decorator
        if is_decorator or current_line.is_def or current_line.is_class:
            if not is_decorator:
                self.previous_defs.append(depth)
            if self.previous_line is None:
                # Don't insert empty lines before the first line in the file.
                return 0, 0

            if self.previous_line.is_decorator:
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
                        newlines = 0
                    else:
                        newlines = 1
                else:
                    newlines = 0
            else:
                newlines = 2
            if current_line.depth and newlines:
                newlines -= 1
            return newlines, 0

        if (
            self.previous_line
            and self.previous_line.is_import
            and not current_line.is_import
            and depth == self.previous_line.depth
        ):
            return (before or 1), 0

        return before, 0


@dataclass
class LineGenerator(Visitor[Line]):
    """Generates reformatted Line objects.  Empty lines are not emitted.

    Note: destroys the tree it's visiting by mutating prefixes of its leaves
    in ways that will no longer stringify to valid Python code on the tree.
    """
    is_pyi: bool = False
    current_line: Line = Factory(Line)
    remove_u_prefix: bool = False

    def line(self, indent: int = 0, type: Type[Line] = Line) -> Iterator[Line]:
        """Generate a line.

        If the line is empty, only emit if it makes sense.
        If the line is too long, split it first and then generate.

        If any lines were generated, set up a new current_line.
        """
        if not self.current_line:
            if self.current_line.__class__ == type:
                self.current_line.depth += indent
            else:
                self.current_line = type(depth=self.current_line.depth + indent)
            return  # Line is empty, don't emit. Creating a new one unnecessary.

        complete_line = self.current_line
        self.current_line = type(depth=complete_line.depth + indent)
        yield complete_line

    def visit(self, node: LN) -> Iterator[Line]:
        """Main method to visit `node` and its children.

        Yields :class:`Line` objects.
        """
        if isinstance(self.current_line, UnformattedLines):
            # File contained `# fmt: off`
            yield from self.visit_unformatted(node)

        else:
            yield from super().visit(node)

    def visit_default(self, node: LN) -> Iterator[Line]:
        """Default `visit_*()` implementation. Recurses to children of `node`."""
        if isinstance(node, Leaf):
            any_open_brackets = self.current_line.bracket_tracker.any_open_brackets()
            try:
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

            except FormatOff as f_off:
                f_off.trim_prefix(node)
                yield from self.line(type=UnformattedLines)
                yield from self.visit(node)

            except FormatOn as f_on:
                # This only happens here if somebody says "fmt: on" multiple
                # times in a row.
                f_on.trim_prefix(node)
                yield from self.visit_default(node)

            else:
                normalize_prefix(node, inside_brackets=any_open_brackets)
                if node.type == token.STRING:
                    normalize_string_prefix(node, remove_u_prefix=self.remove_u_prefix)
                    normalize_string_quotes(node)
                if node.type not in WHITESPACE:
                    self.current_line.append(node)
        yield from super().visit_default(node)

    def visit_INDENT(self, node: Node) -> Iterator[Line]:
        """Increase indentation level, maybe yield a line."""
        # In blib2to3 INDENT never holds comments.
        yield from self.line(+1)
        yield from self.visit_default(node)

    def visit_DEDENT(self, node: Node) -> Iterator[Line]:
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
        if self.is_pyi and is_stub_suite(node):
            yield from self.visit(node.children[2])
        else:
            yield from self.visit_default(node)

    def visit_simple_stmt(self, node: Node) -> Iterator[Line]:
        """Visit a statement without nested statements."""
        is_suite_like = node.parent and node.parent.type in STATEMENT
        if is_suite_like:
            if self.is_pyi and is_stub_body(node):
                yield from self.visit_default(node)
            else:
                yield from self.line(+1)
                yield from self.visit_default(node)
                yield from self.line(-1)

        else:
            if not self.is_pyi or not node.parent or not is_stub_suite(node.parent):
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

    def visit_import_from(self, node: Node) -> Iterator[Line]:
        """Visit import_from and maybe put invisible parentheses.

        This is separate from `visit_stmt` because import statements don't
        support arbitrary atoms and thus handling of parentheses is custom.
        """
        check_lpar = False
        for index, child in enumerate(node.children):
            if check_lpar:
                if child.type == token.LPAR:
                    # make parentheses invisible
                    child.value = ""  # type: ignore
                    node.children[-1].value = ""  # type: ignore
                else:
                    # insert invisible parentheses
                    node.insert_child(index, Leaf(token.LPAR, ""))
                    node.append_child(Leaf(token.RPAR, ""))
                break

            check_lpar = (
                child.type == token.NAME and child.value == "import"  # type: ignore
            )

        for child in node.children:
            yield from self.visit(child)

    def visit_SEMI(self, leaf: Leaf) -> Iterator[Line]:
        """Remove a semicolon and put the other statement on a separate line."""
        yield from self.line()

    def visit_ENDMARKER(self, leaf: Leaf) -> Iterator[Line]:
        """End of file. Process outstanding comments and end with a newline."""
        yield from self.visit_default(leaf)
        yield from self.line()

    def visit_unformatted(self, node: LN) -> Iterator[Line]:
        """Used when file contained a `# fmt: off`."""
        if isinstance(node, Node):
            for child in node.children:
                yield from self.visit(child)

        else:
            try:
                self.current_line.append(node)
            except FormatOn as f_on:
                f_on.trim_prefix(node)
                yield from self.line()
                yield from self.visit(node)

            if node.type == token.ENDMARKER:
                # somebody decided not to put a final `# fmt: on`
                yield from self.line()

    def __attrs_post_init__(self) -> None:
        """You are in a twisty little maze of passages."""
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
        self.visit_async_funcdef = self.visit_async_stmt
        self.visit_decorated = self.visit_decorators


IMPLICIT_TUPLE = {syms.testlist, syms.testlist_star_expr, syms.exprlist}
BRACKET = {token.LPAR: token.RPAR, token.LSQB: token.RSQB, token.LBRACE: token.RBRACE}
OPENING_BRACKETS = set(BRACKET.keys())
CLOSING_BRACKETS = set(BRACKET.values())
BRACKETS = OPENING_BRACKETS | CLOSING_BRACKETS
ALWAYS_NO_SPACE = CLOSING_BRACKETS | {token.COMMA, STANDALONE_COMMENT}


def whitespace(leaf: Leaf, *, complex_subscript: bool) -> str:  # noqa C901
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

        elif prevp.type in STARS:
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

        elif prev.type in {token.EQUAL} | STARS:
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

        elif t == token.NAME or t == token.NUMBER:
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


def child_towards(ancestor: Node, descendant: LN) -> Optional[LN]:
    """Return the child of `ancestor` that contains `descendant`."""
    node: Optional[LN] = descendant
    while node and node.parent != ancestor:
        node = node.parent
    return node


def is_split_after_delimiter(leaf: Leaf, previous: Leaf = None) -> int:
    """Return the priority of the `leaf` delimiter, given a line break after it.

    The delimiter priorities returned here are from those delimiters that would
    cause a line break after themselves.

    Higher numbers are higher priority.
    """
    if leaf.type == token.COMMA:
        return COMMA_PRIORITY

    return 0


def is_split_before_delimiter(leaf: Leaf, previous: Leaf = None) -> int:
    """Return the priority of the `leaf` delimiter, given a line before after it.

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

    if leaf.type != token.NAME:
        return 0

    if (
        leaf.value == "for"
        and leaf.parent
        and leaf.parent.type in {syms.comp_for, syms.old_comp_for}
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


def generate_comments(leaf: Leaf) -> Iterator[Leaf]:
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
    p = leaf.prefix
    if not p:
        return

    if "#" not in p:
        return

    consumed = 0
    nlines = 0
    for index, line in enumerate(p.split("\n")):
        consumed += len(line) + 1  # adding the length of the split '\n'
        line = line.lstrip()
        if not line:
            nlines += 1
        if not line.startswith("#"):
            continue

        if index == 0 and leaf.type != token.ENDMARKER:
            comment_type = token.COMMENT  # simple trailing comment
        else:
            comment_type = STANDALONE_COMMENT
        comment = make_comment(line)
        yield Leaf(comment_type, comment, prefix="\n" * nlines)

        if comment in {"# fmt: on", "# yapf: enable"}:
            raise FormatOn(consumed)

        if comment in {"# fmt: off", "# yapf: disable"}:
            if comment_type == STANDALONE_COMMENT:
                raise FormatOff(consumed)

            prev = preceding_leaf(leaf)
            if not prev or prev.type in WHITESPACE:  # standalone comment in disguise
                raise FormatOff(consumed)

        nlines = 0


def make_comment(content: str) -> str:
    """Return a consistently formatted comment from the given `content` string.

    All comments (except for "##", "#!", "#:") should have a single space between
    the hash sign and the content.

    If `content` didn't start with a hash sign, one is provided.
    """
    content = content.rstrip()
    if not content:
        return "#"

    if content[0] == "#":
        content = content[1:]
    if content and content[0] not in " !:#":
        content = " " + content
    return "#" + content


def split_line(
    line: Line, line_length: int, inner: bool = False, py36: bool = False
) -> Iterator[Line]:
    """Split a `line` into potentially many lines.

    They should fit in the allotted `line_length` but might not be able to.
    `inner` signifies that there were a pair of brackets somewhere around the
    current `line`, possibly transitively. This means we can fallback to splitting
    by delimiters if the LHS/RHS don't yield any results.

    If `py36` is True, splitting may generate syntax that is only compatible
    with Python 3.6 and later.
    """
    if isinstance(line, UnformattedLines) or line.is_comment:
        yield line
        return

    line_str = str(line).strip("\n")
    if not line.should_explode and is_line_short_enough(
        line, line_length=line_length, line_str=line_str
    ):
        yield line
        return

    split_funcs: List[SplitFunc]
    if line.is_def:
        split_funcs = [left_hand_split]
    else:

        def rhs(line: Line, py36: bool = False) -> Iterator[Line]:
            for omit in generate_trailers_to_omit(line, line_length):
                lines = list(right_hand_split(line, line_length, py36, omit=omit))
                if is_line_short_enough(lines[0], line_length=line_length):
                    yield from lines
                    return

            # All splits failed, best effort split with no omits.
            # This mostly happens to multiline strings that are by definition
            # reported as not fitting a single line.
            yield from right_hand_split(line, py36)

        if line.inside_brackets:
            split_funcs = [delimiter_split, standalone_comment_split, rhs]
        else:
            split_funcs = [rhs]
    for split_func in split_funcs:
        # We are accumulating lines in `result` because we might want to abort
        # mission and return the original line in the end, or attempt a different
        # split altogether.
        result: List[Line] = []
        try:
            for l in split_func(line, py36):
                if str(l).strip("\n") == line_str:
                    raise CannotSplit("Split function returned an unchanged result")

                result.extend(
                    split_line(l, line_length=line_length, inner=True, py36=py36)
                )
        except CannotSplit as cs:
            continue

        else:
            yield from result
            break

    else:
        yield line


def left_hand_split(line: Line, py36: bool = False) -> Iterator[Line]:
    """Split line into many lines, starting with the first matching bracket pair.

    Note: this usually looks weird, only use this for function definitions.
    Prefer RHS otherwise.  This is why this function is not symmetrical with
    :func:`right_hand_split` which also handles optional parentheses.
    """
    head = Line(depth=line.depth)
    body = Line(depth=line.depth + 1, inside_brackets=True)
    tail = Line(depth=line.depth)
    tail_leaves: List[Leaf] = []
    body_leaves: List[Leaf] = []
    head_leaves: List[Leaf] = []
    current_leaves = head_leaves
    matching_bracket = None
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
    # Since body is a new indent level, remove spurious leading whitespace.
    if body_leaves:
        normalize_prefix(body_leaves[0], inside_brackets=True)
    # Build the new lines.
    for result, leaves in (head, head_leaves), (body, body_leaves), (tail, tail_leaves):
        for leaf in leaves:
            result.append(leaf, preformatted=True)
            for comment_after in line.comments_after(leaf):
                result.append(comment_after, preformatted=True)
    bracket_split_succeeded_or_raise(head, body, tail)
    for result in (head, body, tail):
        if result:
            yield result


def right_hand_split(
    line: Line, line_length: int, py36: bool = False, omit: Collection[LeafID] = ()
) -> Iterator[Line]:
    """Split line into many lines, starting with the last matching bracket pair.

    If the split was by optional parentheses, attempt splitting without them, too.
    `omit` is a collection of closing bracket IDs that shouldn't be considered for
    this split.

    Note: running this function modifies `bracket_depth` on the leaves of `line`.
    """
    head = Line(depth=line.depth)
    body = Line(depth=line.depth + 1, inside_brackets=True)
    tail = Line(depth=line.depth)
    tail_leaves: List[Leaf] = []
    body_leaves: List[Leaf] = []
    head_leaves: List[Leaf] = []
    current_leaves = tail_leaves
    opening_bracket = None
    closing_bracket = None
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
    tail_leaves.reverse()
    body_leaves.reverse()
    head_leaves.reverse()
    # Since body is a new indent level, remove spurious leading whitespace.
    if body_leaves:
        normalize_prefix(body_leaves[0], inside_brackets=True)
    if not head_leaves:
        # No `head` means the split failed. Either `tail` has all content or
        # the matching `opening_bracket` wasn't available on `line` anymore.
        raise CannotSplit("No brackets found")

    # Build the new lines.
    for result, leaves in (head, head_leaves), (body, body_leaves), (tail, tail_leaves):
        for leaf in leaves:
            result.append(leaf, preformatted=True)
            for comment_after in line.comments_after(leaf):
                result.append(comment_after, preformatted=True)
    bracket_split_succeeded_or_raise(head, body, tail)
    assert opening_bracket and closing_bracket
    if (
        # the opening bracket is an optional paren
        opening_bracket.type == token.LPAR
        and not opening_bracket.value
        # the closing bracket is an optional paren
        and closing_bracket.type == token.RPAR
        and not closing_bracket.value
        # there are no standalone comments in the body
        and not line.contains_standalone_comments(0)
        # and it's not an import (optional parens are the only thing we can split
        # on in this case; attempting a split without them is a waste of time)
        and not line.is_import
    ):
        omit = {id(closing_bracket), *omit}
        if can_omit_invisible_parens(body, line_length):
            try:
                yield from right_hand_split(line, line_length, py36=py36, omit=omit)
                return
            except CannotSplit:
                pass

    ensure_visible(opening_bracket)
    ensure_visible(closing_bracket)
    body.should_explode = should_explode(body, opening_bracket)
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
                f"Splitting brackets on an empty body to save "
                f"{tail_len} characters is not worth it"
            )


def dont_increase_indentation(split_func: SplitFunc) -> SplitFunc:
    """Normalize prefix of the first leaf in every line returned by `split_func`.

    This is a decorator over relevant split functions.
    """

    @wraps(split_func)
    def split_wrapper(line: Line, py36: bool = False) -> Iterator[Line]:
        for l in split_func(line, py36):
            normalize_prefix(l.leaves[0], inside_brackets=True)
            yield l

    return split_wrapper


@dont_increase_indentation
def delimiter_split(line: Line, py36: bool = False) -> Iterator[Line]:
    """Split according to delimiters of the highest priority.

    If `py36` is True, the split will add trailing commas also in function
    signatures that contain `*` and `**`.
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

    current_line = Line(depth=line.depth, inside_brackets=line.inside_brackets)
    lowest_depth = sys.maxsize
    trailing_comma_safe = True

    def append_to_line(leaf: Leaf) -> Iterator[Line]:
        """Append `leaf` to current line or to new line if appending impossible."""
        nonlocal current_line
        try:
            current_line.append_safe(leaf, preformatted=True)
        except ValueError as ve:
            yield current_line

            current_line = Line(depth=line.depth, inside_brackets=line.inside_brackets)
            current_line.append(leaf)

    for index, leaf in enumerate(line.leaves):
        yield from append_to_line(leaf)

        for comment_after in line.comments_after(leaf, index):
            yield from append_to_line(comment_after)

        lowest_depth = min(lowest_depth, leaf.bracket_depth)
        if leaf.bracket_depth == lowest_depth and is_vararg(
            leaf, within=VARARGS_PARENTS
        ):
            trailing_comma_safe = trailing_comma_safe and py36
        leaf_priority = bt.delimiters.get(id(leaf))
        if leaf_priority == delimiter_priority:
            yield current_line

            current_line = Line(depth=line.depth, inside_brackets=line.inside_brackets)
    if current_line:
        if (
            trailing_comma_safe
            and delimiter_priority == COMMA_PRIORITY
            and current_line.leaves[-1].type != token.COMMA
            and current_line.leaves[-1].type != STANDALONE_COMMENT
        ):
            current_line.append(Leaf(token.COMMA, ","))
        yield current_line


@dont_increase_indentation
def standalone_comment_split(line: Line, py36: bool = False) -> Iterator[Line]:
    """Split standalone comments from the rest of the line."""
    if not line.contains_standalone_comments(0):
        raise CannotSplit("Line does not have any standalone comments")

    current_line = Line(depth=line.depth, inside_brackets=line.inside_brackets)

    def append_to_line(leaf: Leaf) -> Iterator[Line]:
        """Append `leaf` to current line or to new line if appending impossible."""
        nonlocal current_line
        try:
            current_line.append_safe(leaf, preformatted=True)
        except ValueError as ve:
            yield current_line

            current_line = Line(depth=line.depth, inside_brackets=line.inside_brackets)
            current_line.append(leaf)

    for index, leaf in enumerate(line.leaves):
        yield from append_to_line(leaf)

        for comment_after in line.comments_after(leaf, index):
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
    match = re.match(r"^([furbFURB]*)(.*)$", leaf.value, re.DOTALL)
    assert match is not None, f"failed to match string {leaf.value!r}"
    orig_prefix = match.group(1)
    new_prefix = orig_prefix.lower()
    if remove_u_prefix:
        new_prefix = new_prefix.replace("u", "")
    leaf.value = f"{new_prefix}{match.group(2)}"


def normalize_string_quotes(leaf: Leaf) -> None:
    """Prefer double quotes but only if it doesn't cause more escaping.

    Adds or removes backslashes as appropriate. Doesn't parse and fix
    strings nested in f-strings (yet).

    Note: Mutates its argument.
    """
    value = leaf.value.lstrip("furbFURB")
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
    escaped_new_quote = re.compile(rf"([^\\]|^)\\(\\\\)*{new_quote}")
    escaped_orig_quote = re.compile(rf"([^\\]|^)\\(\\\\)*{orig_quote}")
    body = leaf.value[first_quote_pos + len(orig_quote) : -len(orig_quote)]
    if "r" in prefix.casefold():
        if unescaped_new_quote.search(body):
            # There's at least one unescaped new_quote in this raw string
            # so converting is impossible
            return

        # Do not introduce or remove backslashes in raw strings
        new_body = body
    else:
        # remove unnecessary quotes
        new_body = sub_twice(escaped_new_quote, rf"\1\2{new_quote}", body)
        if body != new_body:
            # Consider the string without unnecessary quotes as the original
            body = new_body
            leaf.value = f"{prefix}{orig_quote}{body}{orig_quote}"
        new_body = sub_twice(escaped_orig_quote, rf"\1\2{orig_quote}", new_body)
        new_body = sub_twice(unescaped_new_quote, rf"\1\\{new_quote}", new_body)
    if new_quote == '"""' and new_body[-1] == '"':
        # edge case:
        new_body = new_body[:-1] + '\\"'
    orig_escape_count = body.count("\\")
    new_escape_count = new_body.count("\\")
    if new_escape_count > orig_escape_count:
        return  # Do not introduce more escaping

    if new_escape_count == orig_escape_count and orig_quote == '"':
        return  # Prefer double quotes

    leaf.value = f"{prefix}{new_quote}{new_body}{new_quote}"


def normalize_invisible_parens(node: Node, parens_after: Set[str]) -> None:
    """Make existing optional parentheses invisible or create new ones.

    `parens_after` is a set of string leaf values immeditely after which parens
    should be put.

    Standardizes on visible parentheses for single-element tuples, and keeps
    existing visible parentheses for other tuples and generator expressions.
    """
    check_lpar = False
    for child in list(node.children):
        if check_lpar:
            if child.type == syms.atom:
                maybe_make_parens_invisible_in_atom(child)
            elif is_one_tuple(child):
                # wrap child in visible parentheses
                lpar = Leaf(token.LPAR, "(")
                rpar = Leaf(token.RPAR, ")")
                index = child.remove() or 0
                node.insert_child(index, Node(syms.atom, [lpar, child, rpar]))
            elif not (isinstance(child, Leaf) and is_multiline_string(child)):
                # wrap child in invisible parentheses
                lpar = Leaf(token.LPAR, "")
                rpar = Leaf(token.RPAR, "")
                index = child.remove() or 0
                node.insert_child(index, Node(syms.atom, [lpar, child, rpar]))

        check_lpar = isinstance(child, Leaf) and child.value in parens_after


def maybe_make_parens_invisible_in_atom(node: LN) -> bool:
    """If it's safe, make the parens in the atom `node` invisible, recusively."""
    if (
        node.type != syms.atom
        or is_empty_tuple(node)
        or is_one_tuple(node)
        or is_yield(node)
        or max_delimiter_priority_in_atom(node) >= COMMA_PRIORITY
    ):
        return False

    first = node.children[0]
    last = node.children[-1]
    if first.type == token.LPAR and last.type == token.RPAR:
        # make parentheses invisible
        first.value = ""  # type: ignore
        last.value = ""  # type: ignore
        if len(node.children) > 1:
            maybe_make_parens_invisible_in_atom(node.children[1])
        return True

    return False


def is_empty_tuple(node: LN) -> bool:
    """Return True if `node` holds an empty tuple."""
    return (
        node.type == syms.atom
        and len(node.children) == 2
        and node.children[0].type == token.LPAR
        and node.children[1].type == token.RPAR
    )


def is_one_tuple(node: LN) -> bool:
    """Return True if `node` holds a tuple with one element, with or without parens."""
    if node.type == syms.atom:
        if len(node.children) != 3:
            return False

        lpar, gexp, rpar = node.children
        if not (
            lpar.type == token.LPAR
            and gexp.type == syms.testlist_gexp
            and rpar.type == token.RPAR
        ):
            return False

        return len(gexp.children) == 2 and gexp.children[1].type == token.COMMA

    return (
        node.type in IMPLICIT_TUPLE
        and len(node.children) == 2
        and node.children[1].type == token.COMMA
    )


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
    if leaf.type not in STARS or not leaf.parent:
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
    value = leaf.value.lstrip("furbFURB")
    return value[:3] in {'"""', "'''"} and "\n" in value


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


def max_delimiter_priority_in_atom(node: LN) -> int:
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
    :func:`normalize_invible_parens` and :func:`visit_import_from`).
    """
    if leaf.type == token.LPAR:
        leaf.value = "("
    elif leaf.type == token.RPAR:
        leaf.value = ")"


def should_explode(line: Line, opening_bracket: Leaf) -> bool:
    """Should `line` immediately be split with `delimiter_split()` after RHS?"""
    if not (
        opening_bracket.parent
        and opening_bracket.parent.type in {syms.atom, syms.import_from}
        and opening_bracket.value in "[{("
    ):
        return False

    try:
        last_leaf = line.leaves[-1]
        exclude = {id(last_leaf)} if last_leaf.type == token.COMMA else set()
        max_priority = line.bracket_tracker.max_delimiter_priority(exclude=exclude)
    except (IndexError, ValueError):
        return False

    return max_priority == COMMA_PRIORITY


def is_python36(node: Node) -> bool:
    """Return True if the current file is using Python 3.6+ features.

    Currently looking for:
    - f-strings; and
    - trailing commas after * or ** in function signatures and calls.
    """
    for n in node.pre_order():
        if n.type == token.STRING:
            value_head = n.value[:2]  # type: ignore
            if value_head in {'f"', 'F"', "f'", "F'", "rf", "fr", "RF", "FR"}:
                return True

        elif (
            n.type in {syms.typedargslist, syms.arglist}
            and n.children
            and n.children[-1].type == token.COMMA
        ):
            for ch in n.children:
                if ch.type in STARS:
                    return True

                if ch.type == syms.argument:
                    for argch in ch.children:
                        if argch.type in STARS:
                            return True

    return False


def generate_trailers_to_omit(line: Line, line_length: int) -> Iterator[Set[LeafID]]:
    """Generate sets of closing bracket IDs that should be omitted in a RHS.

    Brackets can be omitted if the entire trailer up to and including
    a preceding closing bracket fits in one line.

    Yielded sets are cumulative (contain results of previous yields, too).  First
    set is empty.
    """

    omit: Set[LeafID] = set()
    yield omit

    length = 4 * line.depth
    opening_bracket = None
    closing_bracket = None
    optional_brackets: Set[LeafID] = set()
    inner_brackets: Set[LeafID] = set()
    for index, leaf, leaf_length in enumerate_with_length(line, reversed=True):
        length += leaf_length
        if length > line_length:
            break

        optional_brackets.discard(id(leaf))
        if opening_bracket:
            if leaf is opening_bracket:
                opening_bracket = None
            elif leaf.type in CLOSING_BRACKETS:
                inner_brackets.add(id(leaf))
        elif leaf.type in CLOSING_BRACKETS:
            if not leaf.value:
                optional_brackets.add(id(opening_bracket))
                continue

            if index > 0 and line.leaves[index - 1].type in OPENING_BRACKETS:
                # Empty brackets would fail a split so treat them as "inner"
                # brackets (e.g. only add them to the `omit` set if another
                # pair of brackets was good enough.
                inner_brackets.add(id(leaf))
                continue

            opening_bracket = leaf.opening_bracket
            if closing_bracket:
                omit.add(id(closing_bracket))
                omit.update(inner_brackets)
                inner_brackets.clear()
                yield omit
            closing_bracket = leaf


def get_future_imports(node: Node) -> Set[str]:
    """Return a set of __future__ imports in the file."""
    imports = set()
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
            else:
                break
        elif first_child.type == syms.import_from:
            module_name = first_child.children[1]
            if not isinstance(module_name, Leaf) or module_name.value != "__future__":
                break
            for import_from_child in first_child.children[3:]:
                if isinstance(import_from_child, Leaf):
                    if import_from_child.type == token.NAME:
                        imports.add(import_from_child.value)
                else:
                    assert import_from_child.type == syms.import_as_names
                    for leaf in import_from_child.children:
                        if isinstance(leaf, Leaf) and leaf.type == token.NAME:
                            imports.add(leaf.value)
        else:
            break
    return imports


PYTHON_EXTENSIONS = {".py", ".pyi"}
BLACKLISTED_DIRECTORIES = {
    "build",
    "buck-out",
    "dist",
    "_build",
    ".git",
    ".hg",
    ".mypy_cache",
    ".tox",
    ".venv",
}


def gen_python_files_in_dir(path: Path) -> Iterator[Path]:
    """Generate all files under `path` which aren't under BLACKLISTED_DIRECTORIES
    and have one of the PYTHON_EXTENSIONS.
    """
    for child in path.iterdir():
        if child.is_dir():
            if child.name in BLACKLISTED_DIRECTORIES:
                continue

            yield from gen_python_files_in_dir(child)

        elif child.is_file() and child.suffix in PYTHON_EXTENSIONS:
            yield child


@dataclass
class Report:
    """Provides a reformatting counter. Can be rendered with `str(report)`."""
    check: bool = False
    quiet: bool = False
    change_count: int = 0
    same_count: int = 0
    failure_count: int = 0

    def done(self, src: Path, changed: Changed) -> None:
        """Increment the counter for successful reformatting. Write out a message."""
        if changed is Changed.YES:
            reformatted = "would reformat" if self.check else "reformatted"
            if not self.quiet:
                out(f"{reformatted} {src}")
            self.change_count += 1
        else:
            if not self.quiet:
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

    @property
    def return_code(self) -> int:
        """Return the exit code that the app should use.

        This considers the current state of changed files and failures:
        - if there were any failures, return 123;
        - if any files were changed and --check is being used, return 1;
        - otherwise return 0.
        """
        # According to http://tldp.org/LDP/abs/html/exitcodes.html starting with
        # 126 we have special returncodes reserved by the shell.
        if self.failure_count:
            return 123

        elif self.change_count and self.check:
            return 1

        return 0

    def __str__(self) -> str:
        """Render a color report of the current state.

        Use `click.unstyle` to remove colors.
        """
        if self.check:
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


def assert_equivalent(src: str, dst: str) -> None:
    """Raise AssertionError if `src` and `dst` aren't equivalent."""

    import ast
    import traceback

    def _v(node: ast.AST, depth: int = 0) -> Iterator[str]:
        """Simple visitor generating strings to compare ASTs by content."""
        yield f"{'  ' * depth}{node.__class__.__name__}("

        for field in sorted(node._fields):
            try:
                value = getattr(node, field)
            except AttributeError:
                continue

            yield f"{'  ' * (depth+1)}{field}="

            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        yield from _v(item, depth + 2)

            elif isinstance(value, ast.AST):
                yield from _v(value, depth + 2)

            else:
                yield f"{'  ' * (depth+2)}{value!r},  # {value.__class__.__name__}"

        yield f"{'  ' * depth})  # /{node.__class__.__name__}"

    try:
        src_ast = ast.parse(src)
    except Exception as exc:
        major, minor = sys.version_info[:2]
        raise AssertionError(
            f"cannot use --safe with this file; failed to parse source file "
            f"with Python {major}.{minor}'s builtin AST. Re-run with --fast "
            f"or stop using deprecated Python 2 syntax. AST error message: {exc}"
        )

    try:
        dst_ast = ast.parse(dst)
    except Exception as exc:
        log = dump_to_file("".join(traceback.format_tb(exc.__traceback__)), dst)
        raise AssertionError(
            f"INTERNAL ERROR: Black produced invalid code: {exc}. "
            f"Please report a bug on https://github.com/ambv/black/issues.  "
            f"This invalid output might be helpful: {log}"
        ) from None

    src_ast_str = "\n".join(_v(src_ast))
    dst_ast_str = "\n".join(_v(dst_ast))
    if src_ast_str != dst_ast_str:
        log = dump_to_file(diff(src_ast_str, dst_ast_str, "src", "dst"))
        raise AssertionError(
            f"INTERNAL ERROR: Black produced code that is not equivalent to "
            f"the source.  "
            f"Please report a bug on https://github.com/ambv/black/issues.  "
            f"This diff might be helpful: {log}"
        ) from None


def assert_stable(src: str, dst: str, line_length: int, is_pyi: bool = False) -> None:
    """Raise AssertionError if `dst` reformats differently the second time."""
    newdst = format_str(dst, line_length=line_length, is_pyi=is_pyi)
    if dst != newdst:
        log = dump_to_file(
            diff(src, dst, "source", "first pass"),
            diff(dst, newdst, "first pass", "second pass"),
        )
        raise AssertionError(
            f"INTERNAL ERROR: Black produced different code on the second pass "
            f"of the formatter.  "
            f"Please report a bug on https://github.com/ambv/black/issues.  "
            f"This diff might be helpful: {log}"
        ) from None


def dump_to_file(*output: str) -> str:
    """Dump `output` to a temporary file. Return path to the file."""
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", prefix="blk_", suffix=".log", delete=False, encoding="utf8"
    ) as f:
        for lines in output:
            f.write(lines)
            if lines and lines[-1] != "\n":
                f.write("\n")
    return f.name


def diff(a: str, b: str, a_name: str, b_name: str) -> str:
    """Return a unified diff string between strings `a` and `b`."""
    import difflib

    a_lines = [line + "\n" for line in a.split("\n")]
    b_lines = [line + "\n" for line in b.split("\n")]
    return "".join(
        difflib.unified_diff(a_lines, b_lines, fromfile=a_name, tofile=b_name, n=5)
    )


def cancel(tasks: Iterable[asyncio.Task]) -> None:
    """asyncio signal handler that cancels all `tasks` and reports to stderr."""
    err("Aborted!")
    for task in tasks:
        task.cancel()


def shutdown(loop: BaseEventLoop) -> None:
    """Cancel all pending tasks on `loop`, wait for them, and close the loop."""
    try:
        # This part is borrowed from asyncio/runners.py in Python 3.7b2.
        to_cancel = [task for task in asyncio.Task.all_tasks(loop) if not task.done()]
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

        comment: Optional[Leaf]
        for comment in line.comments_after(leaf, index):
            if "\n" in comment.prefix:
                return  # Oops, standalone comment!

            length += len(comment.value)

        yield index, leaf, length


def is_line_short_enough(line: Line, *, line_length: int, line_str: str = "") -> bool:
    """Return True if `line` is no longer than `line_length`.

    Uses the provided `line_str` rendering, if any, otherwise computes a new one.
    """
    if not line_str:
        line_str = str(line).strip("\n")
    return (
        len(line_str) <= line_length
        and "\n" not in line_str  # multiline strings
        and not line.contains_standalone_comments()
    )


def can_omit_invisible_parens(line: Line, line_length: int) -> bool:
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

    first = line.leaves[0]
    second = line.leaves[1]
    penultimate = line.leaves[-2]
    last = line.leaves[-1]

    # With a single delimiter, omit if the expression starts or ends with
    # a bracket.
    if first.type in OPENING_BRACKETS and second.type not in CLOSING_BRACKETS:
        remainder = False
        length = 4 * line.depth
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

        # Note: we are not returning False here because a line might have *both*
        # a leading opening bracket and a trailing closing bracket.  If the
        # opening bracket doesn't match our rule, maybe the closing will.

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


CACHE_DIR = Path(user_cache_dir("black", version=__version__))


def get_cache_file(line_length: int) -> Path:
    return CACHE_DIR / f"cache.{line_length}.pickle"


def read_cache(line_length: int) -> Cache:
    """Read the cache if it exists and is well formed.

    If it is not well formed, the call to write_cache later should resolve the issue.
    """
    cache_file = get_cache_file(line_length)
    if not cache_file.exists():
        return {}

    with cache_file.open("rb") as fobj:
        try:
            cache: Cache = pickle.load(fobj)
        except pickle.UnpicklingError:
            return {}

    return cache


def get_cache_info(path: Path) -> CacheInfo:
    """Return the information used to check if a file is already formatted or not."""
    stat = path.stat()
    return stat.st_mtime, stat.st_size


def filter_cached(
    cache: Cache, sources: Iterable[Path]
) -> Tuple[List[Path], List[Path]]:
    """Split a list of paths into two.

    The first list contains paths of files that modified on disk or are not in the
    cache. The other list contains paths to non-modified files.
    """
    todo, done = [], []
    for src in sources:
        src = src.resolve()
        if cache.get(src) != get_cache_info(src):
            todo.append(src)
        else:
            done.append(src)
    return todo, done


def write_cache(cache: Cache, sources: List[Path], line_length: int) -> None:
    """Update the cache file."""
    cache_file = get_cache_file(line_length)
    try:
        if not CACHE_DIR.exists():
            CACHE_DIR.mkdir(parents=True)
        new_cache = {**cache, **{src.resolve(): get_cache_info(src) for src in sources}}
        with cache_file.open("wb") as fobj:
            pickle.dump(new_cache, fobj, protocol=pickle.HIGHEST_PROTOCOL)
    except OSError:
        pass


if __name__ == "__main__":
    main()
