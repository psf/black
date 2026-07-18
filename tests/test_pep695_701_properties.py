"""Property-based tests for Python 3.12+ syntax that Black must handle safely.

These focus on two features whose interaction with Black's line-splitting and
comment handling is easy to get wrong:

* **PEP 695 type parameters** (``def f[T]``, ``class C[T]``, ``type A[T] = ...``)
  including PEP 696 defaults (``[T = int]``), ``*TypeVarTuple`` and ``**ParamSpec``.
* **PEP 701 f-strings** (quote reuse, nesting, format specs, conversions, ``=`` debug,
  multiline interpolations).

Rather than the generic grammar fuzzing in ``scripts/fuzz.py``, we build *targeted*
Hypothesis strategies that emit valid source exercising exactly these constructs, then
assert the two invariants that matter regardless of the exact formatting choice:

* **Idempotency** — ``black.assert_stable``: formatting the output again is a no-op.
* **AST safety** — ``black.assert_equivalent``: formatting never changes the parse tree.

Every generated snippet is validated with ``compile()`` before it reaches Black, so a
bug in a strategy surfaces as a test error here rather than masquerading as a Black bug.
"""

import sys

import pytest

hypothesis = pytest.importorskip("hypothesis")

from hypothesis import HealthCheck, given, settings  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

import black  # noqa: E402
from black.mode import TargetVersion  # noqa: E402

# assert_equivalent parses with the *running* interpreter's ``ast`` module, so the
# syntax under test has to be parseable by it. PEP 695 type parameters require 3.12,
# PEP 696 defaults require 3.13.
pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 12),
    reason="PEP 695 type parameters require Python 3.12+ to parse",
)

ALLOW_DEFAULTS = sys.version_info >= (3, 13)

# Deterministic settings mirroring scripts/fuzz.py so CI never flakes and the
# filter-heavy strategies don't trip Hypothesis' health checks.
COMMON_SETTINGS = settings(
    max_examples=250,
    derandomize=True,
    deadline=None,
    suppress_health_check=list(HealthCheck),
)

# A small pool of identifiers keeps generated code readable when a case shrinks.
_NAMES = ["T", "U", "V", "W", "Ts", "Us", "P", "Q", "Alpha", "Beta", "LongTypeName"]


# --------------------------------------------------------------------------- #
# Modes
# --------------------------------------------------------------------------- #
def mode_strategy() -> st.SearchStrategy[black.Mode]:
    """Vary the knobs that affect splitting and string normalization.

    ``line_length`` deliberately includes 1 and other small values — those are the
    classic way to shake out stability bugs in the line splitter.
    """
    version_sets = [set()]  # empty == autodetect
    version_sets.append({TargetVersion.PY312})
    if ALLOW_DEFAULTS:
        version_sets.append({TargetVersion.PY313})
    return st.builds(
        black.Mode,
        target_versions=st.sampled_from(version_sets),
        line_length=st.sampled_from([1, 20, 88]) | st.integers(min_value=1, max_value=120),
        string_normalization=st.booleans(),
        magic_trailing_comma=st.booleans(),
        preview=st.booleans(),
    )


# --------------------------------------------------------------------------- #
# PEP 695 / 696 type-parameter strategies
# --------------------------------------------------------------------------- #
_BOUND_EXPRS = ["int", "(int, str)", "(int, str, bytes)", "SomeBound", "int | str"]
_DEFAULT_EXPRS = ["int", "str", "SomeDefault", "list[int]"]


@st.composite
def _type_param(draw: st.DrawFn, name: str, *, with_default: bool) -> str:
    """A single type parameter. ``*Ts`` / ``**P`` never take a bound (SyntaxError)."""
    kind = draw(st.sampled_from(["plain", "tuple", "paramspec"]))
    if kind == "tuple":
        param = f"*{name}"
    elif kind == "paramspec":
        param = f"**{name}"
    else:
        param = name
        # Only a plain TypeVar may carry a bound or a constraint tuple.
        bound = draw(st.sampled_from([None, *_BOUND_EXPRS]))
        if bound is not None:
            param = f"{name}: {bound}"
    if with_default:
        param += f" = {draw(st.sampled_from(_DEFAULT_EXPRS))}"
    return param


@st.composite
def type_param_list(draw: st.DrawFn) -> str:
    """A comma-separated type-param list obeying the defaults-come-last rule.

    A non-default type parameter may not follow a defaulted one (SyntaxError), so we
    pick how many trailing params get defaults and never place a bare one after them.
    """
    count = draw(st.integers(min_value=1, max_value=4))
    names = draw(
        st.lists(
            st.sampled_from(_NAMES), min_size=count, max_size=count, unique=True
        )
    )
    n_default = draw(st.integers(min_value=0, max_value=count)) if ALLOW_DEFAULTS else 0
    first_default = count - n_default
    params = [
        draw(_type_param(name, with_default=i >= first_default))
        for i, name in enumerate(names)
    ]
    trailing = draw(st.booleans())  # magic trailing comma sometimes
    return ", ".join(params) + ("," if trailing else "")


@st.composite
def type_param_source(draw: st.DrawFn) -> str:
    """A whole statement carrying a type-param list, on a def/class/alias."""
    params = draw(type_param_list())
    template = draw(
        st.sampled_from(
            [
                "def f[{p}](x): pass",
                "async def f[{p}](x): pass",
                "def f[{p}](argument_one, argument_two, argument_three): pass",
                "class C[{p}]: pass",
                "class C[{p}](Base, metaclass=Meta): pass",
                "type Alias[{p}] = list[int]",
            ]
        )
    )
    return template.format(p=params) + "\n"


# --------------------------------------------------------------------------- #
# PEP 701 f-string strategies
# --------------------------------------------------------------------------- #
_FSTRING_EXPRS = [
    "a",
    "b",
    "a + b",
    "obj.attr",
    "func(a, b)",
    "1 + 2",
    "d['key']",
    'f"{a}"',  # nested f-string reusing the double quote (PEP 701)
    "f'{b}'",
]
_CONVERSIONS = ["", "!r", "!s", "!a"]
_FORMAT_SPECS = ["", ":>10", ":.2f", ":{width}", ":=^{n}d"]


@st.composite
def _interpolation(draw: st.DrawFn) -> str:
    expr = draw(st.sampled_from(_FSTRING_EXPRS))
    if draw(st.booleans()):
        # `=` debug form. Combine only with a format spec, never a conversion,
        # to stay comfortably inside valid grammar.
        spec = draw(st.sampled_from(["", ":.2f", ":>10"]))
        return "{" + expr + " = " + spec + "}"
    conv = draw(st.sampled_from(_CONVERSIONS))
    spec = draw(st.sampled_from(_FORMAT_SPECS))
    return "{" + expr + conv + spec + "}"


@st.composite
def fstring_source(draw: st.DrawFn) -> str:
    """A statement assigning an f-string built from literal text + interpolations."""
    parts = draw(
        st.lists(
            st.one_of(
                st.sampled_from(["text ", " middle ", "", "{{ escaped }} "]),
                _interpolation(),
            ),
            min_size=1,
            max_size=5,
        )
    )
    body = "".join(parts)
    quote = draw(st.sampled_from(['"', "'", '"""', "'''"]))
    newline = "\n" if quote in ('"""', "'''") and draw(st.booleans()) else ""
    return f"value = f{quote}{newline}{body}{newline}{quote}\n"


# --------------------------------------------------------------------------- #
# Properties
# --------------------------------------------------------------------------- #
def _check(src: str, mode: black.Mode) -> None:
    """Format @src and assert Black kept it stable and AST-equivalent."""
    # Confirm the strategy produced valid Python; a failure here is a test bug.
    compile(src, "<hypothesis>", "exec")

    dst = black.format_str(src, mode=mode)

    # AST safety: the parse tree must be preserved.
    black.assert_equivalent(src, dst)
    # Idempotency: re-formatting the output changes nothing.
    black.assert_stable(src, dst, mode=mode)


@COMMON_SETTINGS
@given(src=type_param_source(), mode=mode_strategy())
def test_type_params_idempotent_and_ast_safe(src: str, mode: black.Mode) -> None:
    _check(src, mode)


@COMMON_SETTINGS
@given(src=fstring_source(), mode=mode_strategy())
def test_fstrings_idempotent_and_ast_safe(src: str, mode: black.Mode) -> None:
    _check(src, mode)
