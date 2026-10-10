"""Tests for the version handling of the GitHub Action in `action/main.py`."""

import ast
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ACTION_MAIN = Path(__file__).parent.parent / "action" / "main.py"

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 11), reason="use_pyproject requires tomllib"
)


def _load_action_functions() -> dict[str, Any]:
    """Return the functions of `action/main.py` without running the action.

    The module creates a virtualenv and runs pip at import time, so only its
    imports, compiled regexes and function definitions are executed.
    """
    tree = ast.parse(ACTION_MAIN.read_text(encoding="utf-8"))
    body: list[ast.stmt] = [
        node
        for node in tree.body
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef))
        or (
            isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "compile"
        )
    ]
    namespace: dict[str, Any] = {}
    exec(
        compile(ast.Module(body=body, type_ignores=[]), str(ACTION_MAIN), "exec"),
        namespace,
    )
    return namespace


@pytest.fixture
def read_required_version(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Callable[[str], str]:
    read: Callable[[], str] = _load_action_functions()[
        "read_version_specifier_from_pyproject"
    ]
    monkeypatch.chdir(tmp_path)

    def run(required_version: str) -> str:
        (tmp_path / "pyproject.toml").write_text(
            f"[tool.black]\nrequired-version = {required_version!r}\n",
            encoding="utf-8",
        )
        return read()

    return run


@pytest.mark.parametrize(
    "required_version, expected",
    [
        ("26.1.0", "==26.1.0"),
        ("26", "~=26.0"),
        (" 26 ", "~=26.0"),
        ("<27", "<27"),
        (">=26,<27", ">=26,<27"),
        ("~=26.1", "~=26.1"),
        ("", ""),
    ],
)
def test_required_version_accepts_specifiers(
    read_required_version: Callable[[str], str], required_version: str, expected: str
) -> None:
    assert read_required_version(required_version) == expected


@pytest.mark.parametrize(
    "required_version",
    [
        "not a version",
        "26.1.0 extra",
        "@ https://example.invalid/black.whl",
        "<27 @ https://example.invalid/black.whl",
    ],
)
def test_required_version_rejects_non_specifiers(
    read_required_version: Callable[[str], str], required_version: str
) -> None:
    with pytest.raises(SystemExit):
        read_required_version(required_version)
