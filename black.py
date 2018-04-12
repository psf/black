#!/usr/bin/env python3

import asyncio
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
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from attr import dataclass, Factory
import click

# lib2to3 fork
from blib2to3.pytree import Node, Leaf, type_repr
from blib2to3 import pygram, pytree
from blib2to3.pgen2 import driver, token
from blib2to3.pgen2.parse import ParseError

__version__ = "18.4a1"
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
        leaf.prefix = leaf.prefix[self.consumed:]

    def leaf_from_consumed(self, leaf: Leaf) -> Leaf:
        """Returns a new Leaf from the consumed part of the prefix."""
        unformatted_prefix = leaf.prefix[:self.consumed]
        return Leaf(token.NEWLINE, unformatted_prefix)


class FormatOn(FormatError):
    """Found a comment like `# fmt: on` in the file."""


class FormatOff(FormatError):
    """Found a comment like `# fmt: off` in the file."""


class WriteBack(Enum):
    NO = 0
    YES = 1
    DIFF = 2


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
    if check and diff:
        exc = click.ClickException("Options --check and --diff are mutually exclusive")
        exc.exit_code = 2
        raise exc

    if check:
        write_back = WriteBack.NO
    elif diff:
        write_back = WriteBack.DIFF
    else:
        write_back = WriteBack.YES
    if len(sources) == 0:
        ctx.exit(0)
    elif len(sources) == 1:
        p = sources[0]
        report = Report(check=check, quiet=quiet)
        try:
            if not p.is_file() and str(p) == "-":
                changed = format_stdin_to_stdout(
                    line_length=line_length, fast=fast, write_back=write_back
                )
            else:
                changed = format_file_in_place(
                    p, line_length=line_length, fast=fast, write_back=write_back
                )
            report.done(p, changed)
        except Exception as exc:
            report.failed(p, str(exc))
        ctx.exit(report.return_code)
    else:
        loop = asyncio.get_event_loop()
        executor = ProcessPoolExecutor(max_workers=os.cpu_count())
        return_code = 1
        try:
            return_code = loop.run_until_complete(
                schedule_formatting(
                    sources, line_length, write_back, fast, quiet, loop, executor
                )
            )
        finally:
            shutdown(loop)
            ctx.exit(return_code)


async def schedule_formatting(
    sources: List[Path],
    line_length: int,
    write_back: WriteBack,
    fast: bool,
    quiet: bool,
    loop: BaseEventLoop,
    executor: Executor,
) -> int:
    """Run formatting of `sources` in parallel using the provided `executor`.

    (Use ProcessPoolExecutors for actual parallelism.)

    `line_length`, `write_back`, and `fast` options are passed to
    :func:`format_file_in_place`.
    """
    lock = None
    if write_back == WriteBack.DIFF:
        # For diff output, we need locks to ensure we don't interleave output
        # from different processes.
        manager = Manager()
        lock = manager.Lock()
    tasks = {
        src: loop.run_in_executor(
            executor, format_file_in_place, src, line_length, fast, write_back, lock
        )
        for src in sources
    }
    _task_values = list(tasks.values())
    loop.add_signal_handler(signal.SIGINT, cancel, _task_values)
    loop.add_signal_handler(signal.SIGTERM, cancel, _task_values)
    await asyncio.wait(tasks.values())
    cancelled = []
    report = Report(check=write_back is WriteBack.NO, quiet=quiet)
    for src, task in tasks.items():
        if not task.done():
            report.failed(src, "timed out, cancelling")
            task.cancel()
            cancelled.append(task)
        elif task.cancelled():
            cancelled.append(task)
        elif task.exception():
            report.failed(src, str(task.exception()))
        else:
            report.done(src, task.result())
    if cancelled:
        await asyncio.gather(*cancelled, loop=loop, return_exceptions=True)
    elif not quiet:
        out("All done! ✨ 🍰 ✨")
    if not quiet:
        click.echo(str(report))
    return report.return_code


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
    with tokenize.open(src) as src_buffer:
        src_contents = src_buffer.read()
    try:
        dst_contents = format_file_contents(
            src_contents, line_length=line_length, fast=fast
        )
    except NothingChanged:
        return False

    if write_back == write_back.YES:
        with open(src, "w", encoding=src_buffer.encoding) as f:
            f.write(dst_contents)
    elif write_back == write_back.DIFF:
        src_name = f"{src.name}  (original)"
        dst_name = f"{src.name}  (formatted)"
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
    src_contents: str, line_length: int, fast: bool
) -> FileContent:
    """Reformat contents a file and return new contents.

    If `fast` is False, additionally confirm that the reformatted code is
    valid by calling :func:`assert_equivalent` and :func:`assert_stable` on it.
    `line_length` is passed to :func:`format_str`.
    """
    if src_contents.strip() == "":
        raise NothingChanged

    dst_contents = format_str(src_contents, line_length=line_length)
    if src_contents == dst_contents:
        raise NothingChanged

    if not fast:
        assert_equivalent(src_contents, dst_contents)
        assert_stable(src_contents, dst_contents, line_length=line_length)
    return dst_contents


def format_str(src_contents: str, line_length: int) -> FileContent:
    """Reformat a string and return new contents.

    `line_length` determines how many characters per line are allowed.
    """
    src_node = lib2to3_parse(src_contents)
    dst_contents = ""
    lines = LineGenerator()
    elt = EmptyLineTracker()
    py36 = is_python36(src_node)
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
    pygram.python_grammar_no_exec_statement,
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
    token.PLUS,
    token.MINUS,
    token.STAR,
    token.SLASH,
    token.VBAR,
    token.AMPER,
    token.PERCENT,
    token.CIRCUMFLEX,
    token.TILDE,
    token.LEFTSHIFT,
    token.RIGHTSHIFT,
    token.DOUBLESTAR,
    token.DOUBLESLASH,
}
VARARGS = {token.STAR, token.DOUBLESTAR}
COMPREHENSION_PRIORITY = 20
COMMA_PRIORITY = 10
LOGIC_PRIORITY = 5
STRING_PRIORITY = 4
COMPARATOR_PRIORITY = 3
MATH_PRIORITY = 1


@dataclass
class BracketTracker:
    """Keeps track of brackets on a line."""

    depth: int = 0
    bracket_match: Dict[Tuple[Depth, NodeType], Leaf] = Factory(dict)
    delimiters: Dict[LeafID, Priority] = Factory(dict)
    previous: Optional[Leaf] = None

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

    def any_open_brackets(self) -> bool:
        """Return True if there is an yet unmatched open bracket on the line."""
        return bool(self.bracket_match)

    def max_delimiter_priority(self, exclude: Iterable[LeafID] = ()) -> int:
        """Return the highest priority of a delimiter found on the line.

        Values are consistent with what `is_delimiter()` returns.
        Raises ValueError on no delimiters.
        """
        return max(v for k, v in self.delimiters.items() if k not in exclude)


@dataclass
class Line:
    """Holds leaves and comments. Can be printed with `str(line)`."""

    depth: int = 0
    leaves: List[Leaf] = Factory(list)
    comments: List[Tuple[Index, Leaf]] = Factory(list)
    bracket_tracker: BracketTracker = Factory(BracketTracker)
    inside_brackets: bool = False
    has_for: bool = False
    _for_loop_variable: bool = False

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

        if self.leaves and not preformatted:
            # Note: at this point leaf.prefix should be empty except for
            # imports, for which we only preserve newlines.
            leaf.prefix += whitespace(leaf)
        if self.inside_brackets or not preformatted:
            self.maybe_decrement_after_for_loop_variable(leaf)
            self.bracket_tracker.mark(leaf)
            self.maybe_remove_trailing_comma(leaf)
            self.maybe_increment_for_loop_variable(leaf)

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
        return (
            (first_leaf.type == token.NAME and first_leaf.value == "def")
            or (
                first_leaf.type == token.ASYNC
                and second_leaf is not None
                and second_leaf.type == token.NAME
                and second_leaf.value == "def"
            )
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

        # For parens let's check if it's safe to remove the comma.  If the
        # trailing one is the only one, we might mistakenly change a tuple
        # into a different type by removing the comma.
        depth = closing.bracket_depth + 1
        commas = 0
        opening = closing.opening_bracket
        for _opening_index, leaf in enumerate(self.leaves):
            if leaf is opening:
                break

        else:
            return False

        for leaf in self.leaves[_opening_index + 1:]:
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

    def maybe_increment_for_loop_variable(self, leaf: Leaf) -> bool:
        """In a for loop, or comprehension, the variables are often unpacks.

        To avoid splitting on the comma in this situation, increase the depth of
        tokens between `for` and `in`.
        """
        if leaf.type == token.NAME and leaf.value == "for":
            self.has_for = True
            self.bracket_tracker.depth += 1
            self._for_loop_variable = True
            return True

        return False

    def maybe_decrement_after_for_loop_variable(self, leaf: Leaf) -> bool:
        """See `maybe_increment_for_loop_variable` above for explanation."""
        if self._for_loop_variable and leaf.type == token.NAME and leaf.value == "in":
            self.bracket_tracker.depth -= 1
            self._for_loop_variable = False
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

    def comments_after(self, leaf: Leaf) -> Iterator[Leaf]:
        """Generate comments that should appear directly after `leaf`."""
        for _leaf_index, _leaf in enumerate(self.leaves):
            if leaf is _leaf:
                break

        else:
            return

        for index, comment_after in self.comments:
            if _leaf_index == index:
                yield comment_after

    def remove_trailing_comma(self) -> None:
        """Remove the trailing comma and moves the comments attached to it."""
        comma_index = len(self.leaves) - 1
        for i in range(len(self.comments)):
            comment_index, comment = self.comments[i]
            if comment_index == comma_index:
                self.comments[i] = (comma_index - 1, comment)
        self.leaves.pop()

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
            max_allowed = 2
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
            before = 1 if depth else 2
        is_decorator = current_line.is_decorator
        if is_decorator or current_line.is_def or current_line.is_class:
            if not is_decorator:
                self.previous_defs.append(depth)
            if self.previous_line is None:
                # Don't insert empty lines before the first line in the file.
                return 0, 0

            if self.previous_line and self.previous_line.is_decorator:
                # Don't insert empty lines between decorators.
                return 0, 0

            newlines = 2
            if current_line.depth:
                newlines -= 1
            return newlines, 0

        if current_line.is_flow_control:
            return before, 1

        if (
            self.previous_line
            and self.previous_line.is_import
            and not current_line.is_import
            and depth == self.previous_line.depth
        ):
            return (before or 1), 0

        if (
            self.previous_line
            and self.previous_line.is_yield
            and (not current_line.is_yield or depth != self.previous_line.depth)
        ):
            return (before or 1), 0

        return before, 0


@dataclass
class LineGenerator(Visitor[Line]):
    """Generates reformatted Line objects.  Empty lines are not emitted.

    Note: destroys the tree it's visiting by mutating prefixes of its leaves
    in ways that will no longer stringify to valid Python code on the tree.
    """
    current_line: Line = Factory(Line)

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
        # DEDENT has no value. Additionally, in blib2to3 it never holds comments.
        yield from self.line(-1)

    def visit_stmt(
        self, node: Node, keywords: Set[str], parens: Set[str]
    ) -> Iterator[Line]:
        """Visit a statement.

        This implementation is shared for `if`, `while`, `for`, `try`, `except`,
        `def`, `with`, `class`, and `assert`.

        The relevant Python language `keywords` for a given statement will be
        NAME leaves within it. This methods puts those on a separate line.

        `parens` holds pairs of nodes where invisible parentheses should be put.
        Keys hold nodes after which opening parentheses should be put, values
        hold nodes before which closing parentheses should be put.
        """
        normalize_invisible_parens(node, parens_after=parens)
        for child in node.children:
            if child.type == token.NAME and child.value in keywords:  # type: ignore
                yield from self.line()

            yield from self.visit(child)

    def visit_simple_stmt(self, node: Node) -> Iterator[Line]:
        """Visit a statement without nested statements."""
        is_suite_like = node.parent and node.parent.type in STATEMENT
        if is_suite_like:
            yield from self.line(+1)
            yield from self.visit_default(node)
            yield from self.line(-1)

        else:
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
        self.visit_if_stmt = partial(v, keywords={"if", "else", "elif"}, parens={"if"})
        self.visit_while_stmt = partial(v, keywords={"while", "else"}, parens={"while"})
        self.visit_for_stmt = partial(v, keywords={"for", "else"}, parens={"for", "in"})
        self.visit_try_stmt = partial(
            v, keywords={"try", "except", "else", "finally"}, parens=Ø
        )
        self.visit_except_clause = partial(v, keywords={"except"}, parens=Ø)
        self.visit_with_stmt = partial(v, keywords={"with"}, parens=Ø)
        self.visit_funcdef = partial(v, keywords={"def"}, parens=Ø)
        self.visit_classdef = partial(v, keywords={"class"}, parens=Ø)
        self.visit_async_funcdef = self.visit_async_stmt
        self.visit_decorated = self.visit_decorators


IMPLICIT_TUPLE = {syms.testlist, syms.testlist_star_expr, syms.exprlist}
BRACKET = {token.LPAR: token.RPAR, token.LSQB: token.RSQB, token.LBRACE: token.RBRACE}
OPENING_BRACKETS = set(BRACKET.keys())
CLOSING_BRACKETS = set(BRACKET.values())
BRACKETS = OPENING_BRACKETS | CLOSING_BRACKETS
ALWAYS_NO_SPACE = CLOSING_BRACKETS | {token.COMMA, STANDALONE_COMMENT}


def whitespace(leaf: Leaf) -> str:  # noqa C901
    """Return whitespace prefix if needed for the given `leaf`."""
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
    if t == token.COLON and p.type not in {syms.subscript, syms.subscriptlist}:
        return NO

    prev = leaf.prev_sibling
    if not prev:
        prevp = preceding_leaf(p)
        if not prevp or prevp.type in OPENING_BRACKETS:
            return NO

        if t == token.COLON:
            return SPACE if prevp.type == token.COMMA else NO

        if prevp.type == token.EQUAL:
            if prevp.parent:
                if prevp.parent.type in {
                    syms.arglist, syms.argument, syms.parameters, syms.varargslist
                }:
                    return NO

                elif prevp.parent.type == syms.typedargslist:
                    # A bit hacky: if the equal sign has whitespace, it means we
                    # previously found it's a typed argument.  So, we're using
                    # that, too.
                    return prevp.prefix

        elif prevp.type == token.DOUBLESTAR:
            if (
                prevp.parent
                and prevp.parent.type in {
                    syms.arglist,
                    syms.argument,
                    syms.dictsetmaker,
                    syms.parameters,
                    syms.typedargslist,
                    syms.varargslist,
                }
            ):
                return NO

        elif prevp.type == token.COLON:
            if prevp.parent and prevp.parent.type in {syms.subscript, syms.sliceop}:
                return NO

        elif (
            prevp.parent
            and prevp.parent.type in {syms.factor, syms.star_expr}
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
        if t == token.RPAR:
            return NO

        if not prev or prev.type != token.COMMA:
            return NO

    elif p.type == syms.varargslist:
        # lambdas
        if t == token.RPAR:
            return NO

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

        elif prev.type == token.EQUAL or prev.type == token.DOUBLESTAR:
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

    elif p.type == syms.subscript:
        # indexing
        if not prev:
            assert p.parent is not None, "subscripts are always parented"
            if p.parent.type == syms.subscriptlist:
                return SPACE

            return NO

        else:
            return NO

    elif p.type == syms.atom:
        if prev and t == token.DOT:
            # dots, but not the first one.
            return NO

    elif (
        p.type == syms.listmaker
        or p.type == syms.testlist_gexp
        or p.type == syms.subscriptlist
    ):
        # list interior, including unpacking
        if not prev:
            return NO

    elif p.type == syms.dictsetmaker:
        # dict and set interior, including unpacking
        if not prev:
            return NO

        if prev.type == token.DOUBLESTAR:
            return NO

    elif p.type in {syms.factor, syms.star_expr}:
        # unary ops
        if not prev:
            prevp = preceding_leaf(p)
            if not prevp or prevp.type in OPENING_BRACKETS:
                return NO

            prevp_parent = prevp.parent
            assert prevp_parent is not None
            if (
                prevp.type == token.COLON
                and prevp_parent.type in {syms.subscript, syms.sliceop}
            ):
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
    if (
        leaf.type in VARARGS
        and leaf.parent
        and leaf.parent.type in {syms.argument, syms.typedargslist, syms.dictsetmaker}
    ):
        # * and ** might also be MATH_OPERATORS but in this case they are not.
        # Don't treat them as a delimiter.
        return 0

    if (
        leaf.type in MATH_OPERATORS
        and leaf.parent
        and leaf.parent.type not in {syms.factor, syms.star_expr}
    ):
        return MATH_PRIORITY

    if leaf.type in COMPARATORS:
        return COMPARATOR_PRIORITY

    if (
        leaf.type == token.STRING
        and previous is not None
        and previous.type == token.STRING
    ):
        return STRING_PRIORITY

    if (
        leaf.type == token.NAME
        and leaf.value == "for"
        and leaf.parent
        and leaf.parent.type in {syms.comp_for, syms.old_comp_for}
    ):
        return COMPREHENSION_PRIORITY

    if (
        leaf.type == token.NAME
        and leaf.value == "if"
        and leaf.parent
        and leaf.parent.type in {syms.comp_if, syms.old_comp_if}
    ):
        return COMPREHENSION_PRIORITY

    if leaf.type == token.NAME and leaf.value in LOGIC_OPERATORS and leaf.parent:
        return LOGIC_PRIORITY

    return 0


def is_delimiter(leaf: Leaf, previous: Leaf = None) -> int:
    """Return the priority of the `leaf` delimiter. Return 0 if not delimiter.

    Higher numbers are higher priority.
    """
    return max(
        is_split_before_delimiter(leaf, previous),
        is_split_after_delimiter(leaf, previous),
    )


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
    if (
        len(line_str) <= line_length
        and "\n" not in line_str  # multiline strings
        and not line.contains_standalone_comments()
    ):
        yield line
        return

    split_funcs: List[SplitFunc]
    if line.is_def:
        split_funcs = [left_hand_split]
    elif line.inside_brackets:
        split_funcs = [delimiter_split, standalone_comment_split, right_hand_split]
    else:
        split_funcs = [right_hand_split]
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
    Prefer RHS otherwise.
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
    line: Line, py36: bool = False, omit: Collection[LeafID] = ()
) -> Iterator[Line]:
    """Split line into many lines, starting with the last matching bracket pair."""
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
    elif not head_leaves:
        # No `head` and no `body` means the split failed. `tail` has all content.
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
        opening_bracket.type == token.LPAR
        and not opening_bracket.value
        and closing_bracket.type == token.RPAR
        and not closing_bracket.value
    ):
        # These parens were optional. If there aren't any delimiters or standalone
        # comments in the body, they were unnecessary and another split without
        # them should be attempted.
        if not (
            body.bracket_tracker.delimiters or line.contains_standalone_comments(0)
        ):
            omit = {id(closing_bracket), *omit}
            yield from right_hand_split(line, py36=py36, omit=omit)
            return

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

    delimiters = line.bracket_tracker.delimiters
    try:
        delimiter_priority = line.bracket_tracker.max_delimiter_priority(
            exclude={id(last_leaf)}
        )
    except ValueError:
        raise CannotSplit("No delimiters found")

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

    for leaf in line.leaves:
        yield from append_to_line(leaf)

        for comment_after in line.comments_after(leaf):
            yield from append_to_line(comment_after)

        lowest_depth = min(lowest_depth, leaf.bracket_depth)
        if (
            leaf.bracket_depth == lowest_depth
            and leaf.type == token.STAR
            or leaf.type == token.DOUBLESTAR
        ):
            trailing_comma_safe = trailing_comma_safe and py36
        leaf_priority = delimiters.get(id(leaf))
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
    body = leaf.value[first_quote_pos + len(orig_quote):-len(orig_quote)]
    unescaped_new_quote = re.compile(rf"(([^\\]|^)(\\\\)*){new_quote}")
    escaped_orig_quote = re.compile(rf"\\(\\\\)*{orig_quote}")
    if "r" in prefix.casefold():
        if unescaped_new_quote.search(body):
            # There's at least one unescaped new_quote in this raw string
            # so converting is impossible
            return

        # Do not introduce or remove backslashes in raw strings
        new_body = body
    else:
        new_body = escaped_orig_quote.sub(rf"\1{orig_quote}", body)
        new_body = unescaped_new_quote.sub(rf"\1\\{new_quote}", new_body)
        # Add escapes again for consecutive occurences of new_quote (sub
        # doesn't match overlapping substrings).
        new_body = unescaped_new_quote.sub(rf"\1\\{new_quote}", new_body)
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

    Standardizes on visible parentheses for single-element tuples, and keeps
    existing visible parentheses for other tuples and generator expressions.
    """
    check_lpar = False
    for child in list(node.children):
        if check_lpar:
            if child.type == syms.atom:
                if not (
                    is_empty_tuple(child)
                    or is_one_tuple(child)
                    or max_delimiter_priority_in_atom(child) >= COMMA_PRIORITY
                ):
                    first = child.children[0]
                    last = child.children[-1]
                    if first.type == token.LPAR and last.type == token.RPAR:
                        # make parentheses invisible
                        first.value = ""  # type: ignore
                        last.value = ""  # type: ignore
            elif is_one_tuple(child):
                # wrap child in visible parentheses
                lpar = Leaf(token.LPAR, "(")
                rpar = Leaf(token.RPAR, ")")
                index = child.remove() or 0
                node.insert_child(index, Node(syms.atom, [lpar, child, rpar]))
            else:
                # wrap child in invisible parentheses
                lpar = Leaf(token.LPAR, "")
                rpar = Leaf(token.RPAR, "")
                index = child.remove() or 0
                node.insert_child(index, Node(syms.atom, [lpar, child, rpar]))

        check_lpar = isinstance(child, Leaf) and child.value in parens_after


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


def max_delimiter_priority_in_atom(node: LN) -> int:
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


def is_python36(node: Node) -> bool:
    """Return True if the current file is using Python 3.6+ features.

    Currently looking for:
    - f-strings; and
    - trailing commas after * or ** in function signatures.
    """
    for n in node.pre_order():
        if n.type == token.STRING:
            value_head = n.value[:2]  # type: ignore
            if value_head in {'f"', 'F"', "f'", "F'", "rf", "fr", "RF", "FR"}:
                return True

        elif (
            n.type == syms.typedargslist
            and n.children
            and n.children[-1].type == token.COMMA
        ):
            for ch in n.children:
                if ch.type == token.STAR or ch.type == token.DOUBLESTAR:
                    return True

    return False


PYTHON_EXTENSIONS = {".py"}
BLACKLISTED_DIRECTORIES = {
    "build", "buck-out", "dist", "_build", ".git", ".hg", ".mypy_cache", ".tox", ".venv"
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

        elif child.suffix in PYTHON_EXTENSIONS:
            yield child


@dataclass
class Report:
    """Provides a reformatting counter. Can be rendered with `str(report)`."""
    check: bool = False
    quiet: bool = False
    change_count: int = 0
    same_count: int = 0
    failure_count: int = 0

    def done(self, src: Path, changed: bool) -> None:
        """Increment the counter for successful reformatting. Write out a message."""
        if changed:
            reformatted = "would reformat" if self.check else "reformatted"
            if not self.quiet:
                out(f"{reformatted} {src}")
            self.change_count += 1
        else:
            if not self.quiet:
                out(f"{src} already well formatted, good job.", bold=False)
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


def assert_stable(src: str, dst: str, line_length: int) -> None:
    """Raise AssertionError if `dst` reformats differently the second time."""
    newdst = format_str(dst, line_length=line_length)
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
        mode="w", prefix="blk_", suffix=".log", delete=False
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


def cancel(tasks: List[asyncio.Task]) -> None:
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


if __name__ == "__main__":
    main()
