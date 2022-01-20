from enum import Enum
from typing import Any

DEFAULT_LINE_LENGTH = 88
DEFAULT_EXCLUDES = r"/(\.direnv|\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|venv|\.svn|_build|buck-out|build|dist)/"  # noqa: B950
DEFAULT_INCLUDES = r"(\.pyi?|\.ipynb)$"
STDIN_PLACEHOLDER = "__BLACK_STDIN_FILENAME__"


class OutputLevels(Enum):
    null: Any = dict()
    trace = dict(fg="cyan", dim=True)
    debug = dict(fg="green", dim=True)
    info = dict(fg="blue")
    success = dict(fg="green", bold=True)
    warning = dict(fg="yellow")
    error = dict(fg="red")
    critical = dict(fg="red", bold=True)
    notice = dict(fg="magenta", bold=True)
