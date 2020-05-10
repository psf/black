import sys
from functools import partial

from black.comments import generate_comments, list_comments
from black.parse import lib2to3_parse
from black.priorities import *
from black.symbols import *
from black.trackers import BracketTracker, Line, is_multiline_string
from black.types import *
from black.util import out
from blib2to3.pgen2 import token
# lib2to3 fork
from blib2to3.pytree import Leaf, Node, type_repr

import regex as re
from dataclasses import dataclass, field


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


def maybe_make_parens_invisible_in_atom(node: LN, parent: LN) -> bool:
    """If it's safe, make the parens in the atom `node` invisible, recursively.
    Additionally, remove repeated, adjacent invisible parens from the atom `node`
    as they are redundant.

    Returns whether the node should itself be wrapped in invisible parentheses.

    """

    def is_empty_tuple(node: LN) -> bool:
        """Return True if `node` holds an empty tuple."""
        return (
            node.type == syms.atom
            and len(node.children) == 2
            and node.children[0].type == token.LPAR
            and node.children[1].type == token.RPAR
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

    if (
        node.type != syms.atom
        or is_empty_tuple(node)
        or is_one_tuple(node)
        or (is_yield(node) and parent.type != syms.expr_stmt)
        or max_delimiter_priority_in_atom(node) >= COMMA_PRIORITY
    ):
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
            if is_walrus_assignment(child):
                continue

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

    def sub_twice(regex: Pattern[str], replacement: str, original: str) -> str:
        """Replace `regex` with `replacement` twice on `original`.

        This is used by string normalization to perform replaces on
        overlapping matches.
        """
        return regex.sub(replacement, regex.sub(replacement, original))

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

    def format_float_or_int_string(text: str) -> str:
        """Formats a float string like "1.0"."""
        if "." not in text:
            return text

        before, after = text.split(".")
        return f"{before or 0}.{after or 0}"

    text = leaf.value.lower()
    if text.startswith(("0o", "0b")):
        # Leave octal and binary literals alone.
        pass
    elif text.startswith("0x"):
        # Change hex literals to upper case.
        before, after = text[:2], text[2:]
        text = f"{before}{after.upper()}"
    elif "e" in text:
        before, after = text.split("e")
        sign = ""
        if after.startswith("-"):
            after = after[1:]
            sign = "-"
        elif after.startswith("+"):
            after = after[1:]
        before = format_float_or_int_string(before)
        text = f"{before}e{sign}{after}"
    elif text.endswith(("j", "l")):
        number = text[:-1]
        suffix = text[-1]
        # Capitalize in "2L" because "l" looks too similar to "1".
        if suffix == "l":
            suffix = "L"
        text = f"{format_float_or_int_string(number)}{suffix}"
    else:
        text = format_float_or_int_string(text)
    leaf.value = text


def is_walrus_assignment(node: LN) -> bool:
    """Return True iff `node` is of the shape ( test := test )"""
    inner = unwrap_singleton_parenthesis(node)
    return inner is not None and inner.type == syms.namedexpr_test


def unwrap_singleton_parenthesis(node: LN) -> Optional[LN]:
    """Returns `wrapped` if `node` is of the shape ( wrapped ).

    Parenthesis can be optional. Returns None otherwise"""
    if len(node.children) != 3:
        return None

    lpar, wrapped, rpar = node.children
    if not (lpar.type == token.LPAR and rpar.type == token.RPAR):
        return None

    return wrapped


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


def fix_docstring(docstring: str, prefix: str) -> str:
    # https://www.python.org/dev/peps/pep-0257/#handling-docstring-indentation
    if not docstring:
        return ""
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
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
    # Return a single string:
    return "\n".join(trimmed)


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


@dataclass
class LineGenerator(Visitor[Line]):
    """Generates reformatted Line objects.  Empty lines are not emitted.

    Note: destroys the tree it's visiting by mutating prefixes of its leaves
    in ways that will no longer stringify to valid Python code on the tree.
    """

    is_pyi: bool = False
    normalize_strings: bool = True
    current_line: Line = field(default_factory=Line)
    remove_u_prefix: bool = False

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
        self.current_line = Line(depth=complete_line.depth + indent)
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
            if self.normalize_strings and node.type == token.STRING:
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
        def prev_siblings_are(
            node: Optional[LN], tokens: List[Optional[NodeType]]
        ) -> bool:
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

        # Check if it's a docstring
        if prev_siblings_are(
            leaf.parent, [None, token.NEWLINE, token.INDENT, syms.simple_stmt]
        ) and is_multiline_string(leaf):
            prefix = "    " * self.current_line.depth
            docstring = fix_docstring(leaf.value[3:-3], prefix)
            leaf.value = leaf.value[0:3] + docstring + leaf.value[-3:]
            normalize_string_quotes(leaf)

        yield from self.visit_default(leaf)

    def __post_init__(self) -> None:
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
        self.visit_import_from = partial(v, keywords=Ø, parens={"import"})
        self.visit_del_stmt = partial(v, keywords=Ø, parens={"del"})
        self.visit_async_funcdef = self.visit_async_stmt
        self.visit_decorated = self.visit_decorators
