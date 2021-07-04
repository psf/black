import ast
from typing import Dict

import secrets
from typing import NamedTuple, List, Tuple
import collections

from typing import Optional


class Replacement(NamedTuple):
    mask: str
    src: str


class UnsupportedMagic(UserWarning):
    """Raise when Magic (e.g. `a = b??`) is not supported."""


def remove_trailing_semicolon(src: str) -> Tuple[str, bool]:
    """Removing trailing semicolon from Jupyter notebook cell."""
    from tokenize_rt import (
        src_to_tokens,
        tokens_to_src,
        NON_CODING_TOKENS,
        reversed_enumerate,
    )

    tokens = src_to_tokens(src)
    trailing_semicolon = False
    for idx, token in reversed_enumerate(tokens):
        if token.name in NON_CODING_TOKENS or token.name == "NEWLINE" or not token.src:
            continue
        if token.name == "OP" and token.src == ";":
            del tokens[idx]
            trailing_semicolon = True
        break
    if not trailing_semicolon:
        return src, False
    return tokens_to_src(tokens), True


def put_trailing_semicolon_back(src: str, has_trailing_semicolon: bool) -> str:
    """Put trailing semicolon back if cell originally had it."""
    from tokenize_rt import (
        src_to_tokens,
        tokens_to_src,
        NON_CODING_TOKENS,
        reversed_enumerate,
    )

    if not has_trailing_semicolon:
        return src
    tokens = src_to_tokens(src)
    for idx, token in reversed_enumerate(tokens):
        if token.name in NON_CODING_TOKENS or token.name == "NEWLINE" or not token.src:
            continue
        tokens[idx] = token._replace(src=token.src + ";")
        break
    else:  # pragma: nocover
        raise AssertionError("Unreachable code")
    return str(tokens_to_src(tokens))


def mask_cell(src: str) -> Tuple[str, List[Replacement]]:
    """Mask IPython magics so content becomes parseable Python code.

    For example,

        %matplotlib inline
        'foo'

    becomes

        "25716f358c32750e"
        'foo'

    The replacements are returned, along with the transformed code.
    """
    replacements: List[Replacement] = []
    try:
        ast.parse(src)
    except SyntaxError:
        # Might have IPython magics, will process below.
        pass
    else:
        # Syntax is fine, nothing to mask, early return.
        return src, replacements

    from IPython.core.inputtransformer2 import TransformerManager

    transformer_manager = TransformerManager()
    transformed = transformer_manager.transform_cell(src)

    transformed, cell_magic_replacements = replace_cell_magics(transformed)
    replacements += cell_magic_replacements

    transformed = transformer_manager.transform_cell(transformed)
    try:
        transformed, magic_replacements = replace_magics(transformed)
    except UnsupportedMagic:
        # will be ignored upstream
        raise SyntaxError
    if len(transformed.splitlines()) != len(src.splitlines()):
        # multiline magic, won't format
        raise SyntaxError

    replacements += magic_replacements
    return transformed, replacements


def get_token(src: str, magic: str) -> str:
    """Return randomly generated token to mask IPython magic with."""
    assert magic
    nbytes = max(len(magic) // 2 - 1, 1)
    token = secrets.token_hex(nbytes)
    while token in src:  # pragma: nocover
        token = secrets.token_hex(nbytes)
    if len(token) + 2 < len(magic):
        token = f"{token}."
    return f'"{token}"'


def replace_cell_magics(src: str) -> Tuple[str, List[Replacement]]:
    """Replace cell magic with token.

    Note that 'src' will already have been processed by IPython's
    TransformerManager().transform_cell.

    Example,

        get_ipython().run_cell_magic('t', '-n1', 'ls =!ls\\n')

    becomes

        "a794."
        ls =!ls

    The replacement, along with the transformed code, is returned.
    """
    replacements: List[Replacement] = []

    tree = ast.parse(src)

    cell_magic_finder = CellMagicFinder()
    cell_magic_finder.visit(tree)
    if not cell_magic_finder.header:
        return src, replacements
    mask = get_token(src, cell_magic_finder.header)
    replacements.append(Replacement(mask=mask, src=cell_magic_finder.header))
    return f"{mask}\n{cell_magic_finder.body}", replacements


def replace_magics(src: str) -> Tuple[str, List[Replacement]]:
    """Replace magics within body of cell.

    Note that 'src' will already have been processed by IPython's
    TransformerManager().transform_cell.

    Example, this

        get_ipython().run_line_magic('matplotlib', 'inline')
        'foo'

    becomes

        "5e67db56d490fd39"
        'foo'

    The replacement, along with the transformed code, are returned.
    """
    replacements = []

    tree = ast.parse(src)

    magic_finder = MagicFinder()
    magic_finder.visit(tree)
    new_srcs = []
    for i, line in enumerate(src.splitlines(), start=1):
        if i in magic_finder.magics:
            magics = magic_finder.magics[i]
            if len(magics) != 1:  # pragma: nocover
                # defensive check
                raise UnsupportedMagic
            col_offset, magic = magic_finder.magics[i][0]
            mask = get_token(src, magic)
            replacements.append(Replacement(mask=mask, src=magic))
            line = line[:col_offset] + mask
        new_srcs.append(line)
    return "\n".join(new_srcs), replacements


def unmask_cell(src: str, replacements: List[Replacement]) -> str:
    """Remove replacements from cell.

    For example

        "9b20"
        foo = bar

    becomes

        %%time
        foo = bar
    """
    for replacement in replacements:
        src = src.replace(replacement.mask, replacement.src)
    return src


def _is_ipython_magic(node: ast.expr) -> bool:
    """Check if attribute is IPython magic.

    Note that the source of the abstract syntax tree
    will already have been processed by IPython's
    TransformerManager().transform_cell.
    """
    return (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Name)
        and node.value.func.id == "get_ipython"
    )


class CellMagicFinder(ast.NodeVisitor):
    """Find cell magics.

    Note that the source of the abstract syntax tree
    will already have been processed by IPython's
    TransformerManager().transform_cell.
    """

    def __init__(self) -> None:
        self.header: Optional[str] = None
        self.body: Optional[str] = None

    def visit_Expr(self, node: ast.Expr) -> None:  # pylint: disable=C0103
        """Find cell magic, extract header and body."""
        if (
            isinstance(node.value, ast.Call)
            and _is_ipython_magic(node.value.func)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "run_cell_magic"
        ):
            args = []
            for arg in node.value.args:
                assert isinstance(arg, ast.Str)
                args.append(arg.s)
            header: Optional[str] = f"%%{args[0]}"
            if args[1]:
                assert header is not None
                header += f" {args[1]}"
            self.header = header
            self.body = args[2]
        self.generic_visit(node)


class MagicFinder(ast.NodeVisitor):
    """Visit cell to look for get_ipython calls.

    Note that the source of the abstract syntax tree
    will already have been processed by IPython's
    TransformerManager().transform_cell.
    """

    def __init__(self) -> None:
        """Record where magics occur."""
        self.magics: Dict[int, List[Tuple[int, str]]] = collections.defaultdict(list)

    def visit_Assign(self, node: ast.Assign) -> None:  # pylint: disable=C0103,R0912
        """Look for system assign magics. Example:

        foo = get_ipython().getoutput('ls')
        """
        if (
            isinstance(node.value, ast.Call)
            and _is_ipython_magic(node.value.func)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "getoutput"
        ):
            args = []
            for arg in node.value.args:
                assert isinstance(arg, ast.Str)
                args.append(arg.s)
            assert args
            src = f"!{args[0]}"
            self.magics[node.value.lineno].append(
                (
                    node.value.col_offset,
                    src,
                )
            )
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:  # pylint: disable=C0103,R0912
        """Look for magics in body of cell. Examples:

        get_ipython().system('ls')
        get_ipython().getoutput('ls')
        get_ipython().run_line_magic('pinfo', 'ls')
        get_ipython().run_line_magic('pinfo2', 'ls')
        """
        if isinstance(node.value, ast.Call) and _is_ipython_magic(node.value.func):
            assert isinstance(node.value.func, ast.Attribute)  # help mypy
            args = []
            for arg in node.value.args:
                assert isinstance(arg, ast.Str)
                args.append(arg.s)
            assert args
            if node.value.func.attr == "run_line_magic":
                if args[0] == "pinfo":
                    src = f"?{args[1]}"
                elif args[0] == "pinfo2":
                    src = f"??{args[1]}"
                else:
                    src = f"%{args[0]}"
                    if args[1]:
                        assert src is not None
                        src += f" {args[1]}"
            elif node.value.func.attr == "system":
                src = f"!{args[0]}"
            elif node.value.func.attr == "getoutput":
                src = f"!!{args[0]}"
            else:
                raise UnsupportedMagic
            self.magics[node.value.lineno].append(
                (
                    node.value.col_offset,
                    src,
                )
            )
        self.generic_visit(node)
