import sys

if sys.version_info < (3, 8):
    from typing_extensions import Final
else:
    from typing import Final


DEFAULT_LINE_LENGTH = 88
DEFAULT_EXCLUDES = r"/(\.direnv|\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|venv|\.svn|_build|buck-out|build|dist)/"  # noqa: B950
DEFAULT_INCLUDES = r"\.pyi?$"
STDIN_PLACEHOLDER = "__BLACK_STDIN_FILENAME__"
STRING_PREFIX_CHARS: Final = "furbFURB"  # All possible string prefix characters.
