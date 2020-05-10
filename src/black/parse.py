import ast
import sys

from black.symbols import *
from black.types import *
from blib2to3 import pygram, pytree
from blib2to3.pgen2 import driver, token
from blib2to3.pgen2.grammar import Grammar
from blib2to3.pgen2.parse import ParseError

import regex as re
from typed_ast import ast3, ast27

ALL_GRAMMARS = [
    # Python 3.7+
    pygram.python_grammar_no_print_statement_no_exec_statement_async_keywords,
    # Python 3.0-3.6
    pygram.python_grammar_no_print_statement_no_exec_statement,
    # Python 2.7 with future print_function import
    pygram.python_grammar_no_print_statement,
    # Python 2.7
    pygram.python_grammar,
]

PYTHON2_GRAMMARS = [
    # Python 2.7 with future print_function import
    pygram.python_grammar_no_print_statement,
    # Python 2.7
    pygram.python_grammar,
]


class InvalidInput(ValueError):
    """Raised when input source code fails all parse attempts."""


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

    return ast27.parse(src)


def lib2to3_parse(src_txt: str, grammars: List[Grammar] = ALL_GRAMMARS) -> Node:
    """Given a string with source, return the lib2to3 Node."""
    if src_txt[-1:] != "\n":
        src_txt += "\n"

    for grammar in grammars:
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


def stringify_ast(
    node: Union[ast.AST, ast3.AST, ast27.AST], depth: int = 0
) -> Iterator[str]:
    """Simple visitor generating strings to compare ASTs by content."""

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
                        yield from stringify_ast(item, depth + 2)

                elif isinstance(item, (ast.AST, ast3.AST, ast27.AST)):
                    yield from stringify_ast(item, depth + 2)

        elif isinstance(value, (ast.AST, ast3.AST, ast27.AST)):
            yield from stringify_ast(value, depth + 2)

        else:
            # Constant strings may be indented across newlines, if they are
            # docstrings; fold spaces after newlines when comparing
            if (
                isinstance(node, ast.Constant)
                and field == "value"
                and isinstance(value, str)
            ):
                normalized = re.sub(r"\n[ \t]+", "\n ", value)
            else:
                normalized = value
            yield f"{'  ' * (depth+2)}{normalized!r},  # {value.__class__.__name__}"

    yield f"{'  ' * depth})  # /{node.__class__.__name__}"


def is_empty_par(leaf: Leaf) -> bool:
    return is_empty_lpar(leaf) or is_empty_rpar(leaf)


def is_empty_lpar(leaf: Leaf) -> bool:
    return leaf.type == token.LPAR and leaf.value == ""


def is_empty_rpar(leaf: Leaf) -> bool:
    return leaf.type == token.RPAR and leaf.value == ""


class StringParser:
    """
    A state machine that aids in parsing a string's "trailer", which can be
    either non-existant, an old-style formatting sequence (e.g. `% varX` or `%
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
            * On the next call to this function, the leaf paramater passed in
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


def lib2to3_unparse(node: Node) -> str:
    """Given a lib2to3 node, return its string representation."""
    code = str(node)
    return code
