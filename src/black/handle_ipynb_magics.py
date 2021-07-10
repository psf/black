"""Functions to process IPython magics with."""
import ast
import tokenize
import io
from typing import Dict

import secrets
from typing import NamedTuple, List, Tuple
import collections

from typing import Optional
from typing_extensions import TypeGuard


class Replacement(NamedTuple):
    mask: str
    src: str


class UnsupportedMagic(UserWarning):
    """Raise when Magic is not supported (e.g. `a = b??`)"""


def remove_trailing_semicolon(src: str) -> Tuple[str, bool]:
    """Remove trailing semicolon from Jupyter notebook cell.

    For example,

        fig, ax = plt.subplots()
        ax.plot(x_data, y_data);  # plot data

    would become

        fig, ax = plt.subplots()
        ax.plot(x_data, y_data)  # plot data

    Mirrors the logic in `quiet` from `IPython.core.displayhook`.
    """
    tokens = list(tokenize.generate_tokens(io.StringIO(src).readline))
    trailing_semicolon = False
    for idx, token in enumerate(reversed(tokens), start=1):
        if token[0] in (
            tokenize.ENDMARKER,
            tokenize.NL,
            tokenize.NEWLINE,
            tokenize.COMMENT,
        ):
            continue
        if token[0] == tokenize.OP and token[1] == ";":
            # We're iterating backwards, so `-idx`.
            del tokens[-idx]
            trailing_semicolon = True
        break
    if not trailing_semicolon:
        return src, False
    return tokenize.untokenize(tokens), True


def put_trailing_semicolon_back(src: str, has_trailing_semicolon: bool) -> str:
    """Put trailing semicolon back if cell originally had it.

    Mirrors the logic in `quiet` from `IPython.core.displayhook`.
    """
    if not has_trailing_semicolon:
        return src
    tokens = list(tokenize.generate_tokens(io.StringIO(src).readline))
    for idx, token in enumerate(reversed(tokens), start=1):
        if token[0] in (
            tokenize.ENDMARKER,
            tokenize.NL,
            tokenize.NEWLINE,
            tokenize.COMMENT,
        ):
            continue
        # We're iterating backwards, so `-idx`.
        tokens[-idx] = token._replace(string=token.string + ";")
        break
    else:  # pragma: nocover
        raise AssertionError("Unreachable code")
    return str(tokenize.untokenize(tokens))


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
        raise SyntaxError
    if len(transformed.splitlines()) != len(src.splitlines()):  # multi-line magic
        raise SyntaxError
    replacements += magic_replacements
    return transformed, replacements


def get_token(src: str, magic: str) -> str:
    """Return randomly generated token to mask IPython magic with.

    For example, if 'magic' was `%matplotlib inline`, then a possible
    token to mask it with would be `"43fdd17f7e5ddc83"`. The token
    will be the same length as the magic, and we make sure that it was
    not already present anywhere else in the cell.
    """
    assert magic
    nbytes = max(len(magic) // 2 - 1, 1)
    token = secrets.token_hex(nbytes)
    counter = 0
    while token in src:  # pragma: nocover
        token = secrets.token_hex(nbytes)
        counter += 1
        if counter > 100:
            raise AssertionError()
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
    magic_finder = MagicFinder()
    magic_finder.visit(ast.parse(src))
    new_srcs = []
    for i, line in enumerate(src.splitlines(), start=1):
        if i in magic_finder.magics:
            magics = magic_finder.magics[i]
            if len(magics) != 1:  # pragma: nocover
                # defensive check
                raise UnsupportedMagic
            col_offset, magic = magics[0]
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


def _is_ipython_magic(node: ast.expr) -> TypeGuard[ast.Attribute]:
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

    For example,

        %%time\nfoo()

    would have been transformed to

        get_ipython().run_cell_magic('time', '', 'foo()\\n')

    and we look for instances of the latter.
    """

    def __init__(self) -> None:
        self.header: Optional[str] = None
        self.body: Optional[str] = None

    def visit_Expr(self, node: ast.Expr) -> None:
        """Find cell magic, extract header and body."""
        if (
            isinstance(node.value, ast.Call)
            and _is_ipython_magic(node.value.func)
            and node.value.func.attr == "run_cell_magic"
        ):
            args = []
            for arg in node.value.args:
                assert isinstance(arg, ast.Str)
                args.append(arg.s)
            header = f"%%{args[0]}"
            if args[1]:
                header += f" {args[1]}"
            self.header = header
            self.body = args[2]
        self.generic_visit(node)


class MagicFinder(ast.NodeVisitor):
    """Visit cell to look for get_ipython calls.

    Note that the source of the abstract syntax tree
    will already have been processed by IPython's
    TransformerManager().transform_cell.

    For example,

        %matplotlib inline

    would have been transformed to

        get_ipython().run_line_magic('matplotlib', 'inline')

    and we look for instances of the latter (and likewise for other
    types of magics).
    """

    def __init__(self) -> None:
        """Record where magics occur."""
        self.magics: Dict[int, List[Tuple[int, str]]] = collections.defaultdict(list)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Look for system assign magics.

        For example,

            black_version = !black --version

        would have been transformed to

            black_version = get_ipython().getoutput('black --version')

        and we look for instances of the latter.
        """
        if (
            isinstance(node.value, ast.Call)
            and _is_ipython_magic(node.value.func)
            and node.value.func.attr == "getoutput"
        ):
            args = []
            for arg in node.value.args:
                assert isinstance(arg, ast.Str)
                args.append(arg.s)
            assert args
            src = f"!{args[0]}"
            self.magics[node.value.lineno].append((node.value.col_offset, src))
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:
        """Look for magics in body of cell.

        For examples,

            !ls
            !!ls
            ?ls
            ??ls

        would (respectively) get transformed to

            get_ipython().system('ls')
            get_ipython().getoutput('ls')
            get_ipython().run_line_magic('pinfo', 'ls')
            get_ipython().run_line_magic('pinfo2', 'ls')

        and we look for instances of any of the latter.
        """
        if isinstance(node.value, ast.Call) and _is_ipython_magic(node.value.func):
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
