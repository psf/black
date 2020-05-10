from enum import Enum

from black.comments import list_comments
from black.defaults import DEFAULT_LINE_LENGTH
from black.parse import (ALL_GRAMMARS, PYTHON2_GRAMMARS, lib2to3_parse,
                         parse_ast, stringify_ast)
from black.symbols import *
from black.trackers import EmptyLineTracker, Line, preceding_leaf
from black.transformers import Feature, transform_line
from black.types import *
from black.util import diff, dump_to_file
from black.visitors import LineGenerator
from blib2to3 import pygram, pytree
from blib2to3.pgen2 import driver, token
from blib2to3.pgen2.grammar import Grammar

from dataclasses import dataclass, field


class NothingChanged(UserWarning):
    """Raised when reformatted code is the same as source."""


class TargetVersion(Enum):
    PY27 = 2
    PY33 = 3
    PY34 = 4
    PY35 = 5
    PY36 = 6
    PY37 = 7
    PY38 = 8

    def is_python2(self) -> bool:
        return self is TargetVersion.PY27


PY36_VERSIONS = {TargetVersion.PY36, TargetVersion.PY37, TargetVersion.PY38}


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
}


def supports_feature(target_versions: Set[TargetVersion], feature: Feature) -> bool:
    return all(feature in VERSION_TO_FEATURES[version] for version in target_versions)


@dataclass
class Mode:
    target_versions: Set[TargetVersion] = field(default_factory=set)
    line_length: int = DEFAULT_LINE_LENGTH
    string_normalization: bool = True
    is_pyi: bool = False

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
        ]
        return ".".join(parts)

    def get_grammars(self) -> List[Grammar]:
        if not self.target_versions:
            # No target_version specified, so try all grammars.
            return ALL_GRAMMARS

        if all(version.is_python2() for version in self.target_versions):
            # Python 2-only code, so try Python 2 grammars.
            return PYTHON2_GRAMMARS

        # Python 3-compatible code, so only try Python 3 grammar.
        grammars = []
        # If we have to parse both, try to parse async as a keyword first
        if not supports_feature(self.target_versions, Feature.ASYNC_IDENTIFIERS):
            # Python 3.7+
            grammars.append(
                pygram.python_grammar_no_print_statement_no_exec_statement_async_keywords
            )
        if not supports_feature(self.target_versions, Feature.ASYNC_KEYWORDS):
            # Python 3.0-3.6
            grammars.append(pygram.python_grammar_no_print_statement_no_exec_statement)
        # At least one of the above branches must have been taken, because every Python
        # version has exactly one of the two 'ASYNC_*' flags
        return grammars


# Legacy name, left for integrations.
FileMode = Mode


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


def get_features_used(node: Node) -> Set[Feature]:
    """Return a set of (relatively) new Python features used in this file.

    Currently looking for:
    - f-strings;
    - underscores in numeric literals;
    - trailing commas after * or ** in function signatures and calls;
    - positional only arguments in function signatures and lambdas;
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


def generate_ignored_nodes(leaf: Leaf) -> Iterator[LN]:
    """Starting from the container of `leaf`, generate all leaves until `# fmt: on`.

    Stops at the end of the block.
    """

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

    container: Optional[LN] = container_of(leaf)
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


# ---- Code Formatter ----


class Formatter:
    """Code formatter.

    `mode` determines formatting options, such as how many characters per line are
    allowed.
    """

    def __init__(self, mode: Mode = None):
        self.mode = mode or Mode()

    def _format(self, src_contents: str) -> FileContent:
        """Reformat a string and return new contents.

        Example:
        >>> import black
        >>> print(black.formatter.Formatter(black.source.Mode()).format("def f(arg:str='')->None:..."))
        def f(arg: str = "") -> None:
            ...

        A more complex example:
        >>> print(
        ...   black.formatter.Formatter(black.source.Mode(
        ...     target_versions={black.formatter.TargetVersion.PY36},
        ...     line_length=10,
        ...     string_normalization=False,
        ...     is_pyi=False,
        ...   ).format(
        ...     "def f(arg:str='')->None: hey",
        ...   )
        ... )
        def f(
            arg: str = '',
        ) -> None:
            hey

        """

        def convert_one_fmt_off_pair(node: Node) -> bool:
            """Convert content of a single `# fmt: off`/`# fmt: on` into a standalone comment.

            Returns True if a pair was converted.
            """
            for leaf in node.leaves():
                previous_consumed = 0
                for comment in list_comments(leaf.prefix, is_endmarker=False):
                    if comment.value in FMT_OFF:
                        # We only want standalone comments. If there's no previous leaf or
                        # the previous leaf is indentation, it's a standalone comment in
                        # disguise.
                        if comment.type != STANDALONE_COMMENT:
                            prev = preceding_leaf(leaf)
                            if prev and prev.type not in WHITESPACE:
                                continue

                        ignored_nodes = list(generate_ignored_nodes(leaf))
                        if not ignored_nodes:
                            continue

                        first = ignored_nodes[
                            0
                        ]  # Can be a container node with the `leaf`.
                        parent = first.parent
                        prefix = first.prefix
                        first.prefix = prefix[comment.consumed :]
                        hidden_value = (
                            comment.value
                            + "\n"
                            + "".join(str(n) for n in ignored_nodes)
                        )
                        if hidden_value.endswith("\n"):
                            # That happens when one of the `ignored_nodes` ended with a NEWLINE
                            # leaf (possibly followed by a DEDENT).
                            hidden_value = hidden_value[:-1]
                        first_idx: Optional[int] = None
                        for ignored in ignored_nodes:
                            index = ignored.remove()
                            if first_idx is None:
                                first_idx = index
                        assert (
                            parent is not None
                        ), "INTERNAL ERROR: fmt: on/off handling (1)"
                        assert (
                            first_idx is not None
                        ), "INTERNAL ERROR: fmt: on/off handling (2)"
                        parent.insert_child(
                            first_idx,
                            Leaf(
                                STANDALONE_COMMENT,
                                hidden_value,
                                prefix=prefix[:previous_consumed]
                                + "\n" * comment.newlines,
                            ),
                        )
                        return True

                    previous_consumed = comment.consumed

            return False

        # TODO: Decorator?
        def normalize_fmt_off(node: Node) -> None:
            """Convert content between `# fmt: off`/`# fmt: on` into standalone comments."""
            try_again = True
            while try_again:
                try_again = convert_one_fmt_off_pair(node)

        mode = self.mode
        src_node = lib2to3_parse(src_contents.lstrip(), mode.get_grammars())
        dst_contents = []
        future_imports = get_future_imports(src_node)
        if mode.target_versions:
            versions = mode.target_versions
        else:
            versions = detect_target_versions(src_node)
        normalize_fmt_off(src_node)
        lines = LineGenerator(
            remove_u_prefix="unicode_literals" in future_imports
            or supports_feature(versions, Feature.UNICODE_LITERALS),
            is_pyi=mode.is_pyi,
            normalize_strings=mode.string_normalization,
        )
        elt = EmptyLineTracker(is_pyi=mode.is_pyi)
        empty_line = Line()
        after = 0
        split_line_features = {
            feature
            for feature in {
                Feature.TRAILING_COMMA_IN_CALL,
                Feature.TRAILING_COMMA_IN_DEF,
            }
            if supports_feature(versions, feature)
        }
        for current_line in lines.visit(src_node):
            dst_contents.append(str(empty_line) * after)
            before, after = elt.maybe_empty_lines(current_line)
            dst_contents.append(str(empty_line) * before)
            for line in transform_line(
                current_line,
                line_length=mode.line_length,
                normalize_strings=mode.string_normalization,
                features=split_line_features,
            ):
                dst_contents.append(str(line))
        return "".join(dst_contents)

    @staticmethod
    def assert_equivalent(src: str, dst: str) -> None:
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
                f"INTERNAL ERROR: Black produced invalid code: {exc}. Please report a bug"
                " on https://github.com/psf/black/issues.  This invalid output might be"
                f" helpful: {log}"
            ) from None

        src_ast_str = "\n".join(stringify_ast(src_ast))
        dst_ast_str = "\n".join(stringify_ast(dst_ast))
        if src_ast_str != dst_ast_str:
            log = dump_to_file(diff(src_ast_str, dst_ast_str, "src", "dst"))
            raise AssertionError(
                "INTERNAL ERROR: Black produced code that is not equivalent to the"
                " source.  Please report a bug on https://github.com/psf/black/issues. "
                f" This diff might be helpful: {log}"
            ) from None

    def assert_stable(self, src: str, dst: str) -> None:
        """Raise AssertionError if `dst` reformats differently the second time."""
        newdst = self._format(dst)
        if dst != newdst:
            log = dump_to_file(
                diff(src, dst, "source", "first pass"),
                diff(dst, newdst, "first pass", "second pass"),
            )
            raise AssertionError(
                "INTERNAL ERROR: Black produced different code on the second pass of the"
                " formatter.  Please report a bug on https://github.com/psf/black/issues."
                f"  This diff might be helpful: {log}"
            ) from None

    def format(self, src_contents: str, *, fast: bool) -> FileContent:
        """Reformat contents a file and return new contents.

        If `fast` is False, additionally confirm that the reformatted code is
        valid by calling :func:`assert_equivalent` and :func:`assert_stable` on it.
        `mode` is passed to :func:`format_str`.
        """

        if src_contents.strip() == "":
            raise NothingChanged

        dst_contents = self._format(src_contents)
        if src_contents == dst_contents:
            raise NothingChanged

        if not fast:
            Formatter.assert_equivalent(src_contents, dst_contents)
            self.assert_stable(src_contents, dst_contents)
        return dst_contents
