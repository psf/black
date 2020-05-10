import itertools
import sys

from black.priorities import *
from black.symbols import *
from black.types import *
from blib2to3.pgen2 import token

from dataclasses import dataclass, field


def is_split_after_delimiter(leaf: Leaf, previous: Optional[Leaf] = None) -> Priority:
    """Return the priority of the `leaf` delimiter, given a line break after it.

    The delimiter priorities returned here are from those delimiters that would
    cause a line break after themselves.

    Higher numbers are higher priority.
    """
    return COMMA_PRIORITY if leaf.type == token.COMMA else 0


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


def has_triple_quotes(string: str) -> bool:
    """
    Returns:
        True iff @string starts with three quotation characters.
    """
    raw_string = string.lstrip(STRING_PREFIX_CHARS)
    return raw_string[:3] in {'"""', "'''"}


def is_multiline_string(leaf: Leaf) -> bool:
    """Return True if `leaf` is a multiline string that actually spans many lines."""
    return has_triple_quotes(leaf.value) and "\n" in leaf.value


def is_type_comment(leaf: Leaf, suffix: str = "") -> bool:
    """Return True if the given leaf is a special comment.
    Only returns true for type comments for now."""
    t = leaf.type
    v = leaf.value
    return t in {token.COMMENT, STANDALONE_COMMENT} and v.startswith("# type:" + suffix)


def child_towards(ancestor: Node, descendant: LN) -> Optional[LN]:
    """Return the child of `ancestor` that contains `descendant`."""
    node: Optional[LN] = descendant
    while node and node.parent != ancestor:
        node = node.parent
    return node


@dataclass
class BracketTracker:
    """Keeps track of brackets on a line."""

    depth: int = 0
    bracket_match: Dict[Tuple[Depth, NodeType], Leaf] = field(default_factory=dict)
    delimiters: Dict[LeafID, Priority] = field(default_factory=dict)
    previous: Optional[Leaf] = None
    _for_loop_depths: List[int] = field(default_factory=list)
    _lambda_argument_depths: List[int] = field(default_factory=list)

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

    depth: int = 0
    leaves: List[Leaf] = field(default_factory=list)
    # keys ordered like `leaves`
    comments: Dict[LeafID, List[Leaf]] = field(default_factory=dict)
    bracket_tracker: BracketTracker = field(default_factory=BracketTracker)
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
    def is_collection_with_optional_trailing_comma(self) -> bool:
        """Is this line a collection literal with a trailing comma that's optional?

        Note that the trailing comma in a 1-tuple is not optional.
        """
        if not self.leaves or len(self.leaves) < 4:
            return False

        # Look for and address a trailing colon.
        if self.leaves[-1].type == token.COLON:
            closer = self.leaves[-2]
            close_index = -2
        else:
            closer = self.leaves[-1]
            close_index = -1
        if closer.type not in CLOSING_BRACKETS or self.inside_brackets:
            return False

        if closer.type == token.RPAR:
            # Tuples require an extra check, because if there's only
            # one element in the tuple removing the comma unmakes the
            # tuple.
            #
            # We also check for parens before looking for the trailing
            # comma because in some cases (eg assigning a dict
            # literal) the literal gets wrapped in temporary parens
            # during parsing. This case is covered by the
            # collections.py test data.
            opener = closer.opening_bracket
            for _open_index, leaf in enumerate(self.leaves):
                if leaf is opener:
                    break

            else:
                # Couldn't find the matching opening paren, play it safe.
                return False

            commas = 0
            comma_depth = self.leaves[close_index - 1].bracket_depth
            for leaf in self.leaves[_open_index + 1 : close_index]:
                if leaf.bracket_depth == comma_depth and leaf.type == token.COMMA:
                    commas += 1
            if commas > 1:
                # We haven't looked yet for the trailing comma because
                # we might also have caught noop parens.
                return self.leaves[close_index - 1].type == token.COMMA

            elif commas == 1:
                return False  # it's either a one-tuple or didn't have a trailing comma

            if self.leaves[close_index - 1].type in CLOSING_BRACKETS:
                close_index -= 1
                closer = self.leaves[close_index]
                if closer.type == token.RPAR:
                    # TODO: this is a gut feeling. Will we ever see this?
                    return False

        if self.leaves[close_index - 1].type != token.COMMA:
            return False

        return True

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
        first_line = next((l.lineno for l in self.leaves if l.lineno != 0), 0)
        last_line = next((l.lineno for l in reversed(self.leaves) if l.lineno != 0), 0)

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

    def maybe_remove_trailing_comma(self, closing: Leaf) -> bool:
        """Remove trailing comma if there is one and it's safe."""
        if not (self.leaves and self.leaves[-1].type == token.COMMA):
            return False

        # We remove trailing commas only in the case of importing a
        # single name from a module.
        if not (
            self.leaves
            and self.is_import
            and len(self.leaves) > 4
            and self.leaves[-1].type == token.COMMA
            and closing.type in CLOSING_BRACKETS
            and self.leaves[-4].type == token.NAME
            and (
                # regular `from foo import bar,`
                self.leaves[-4].value == "import"
                # `from foo import (bar as baz,)
                or (
                    len(self.leaves) > 6
                    and self.leaves[-6].value == "import"
                    and self.leaves[-3].value == "as"
                )
                # `from foo import bar as baz,`
                or (
                    len(self.leaves) > 5
                    and self.leaves[-5].value == "import"
                    and self.leaves[-3].value == "as"
                )
            )
            and closing.type == token.RPAR
        ):
            return False

        self.remove_trailing_comma()
        return True

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
            depth=self.depth,
            inside_brackets=self.inside_brackets,
            should_explode=self.should_explode,
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
            elif current_line.is_def and not self.previous_line.is_def:
                # Blank line between a block of functions and a block of non-functions
                newlines = 1
            else:
                newlines = 0
        else:
            newlines = 2
        if current_line.depth and newlines:
            newlines -= 1
        return newlines, 0
