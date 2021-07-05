DEFAULT_LINE_LENGTH = 88
DEFAULT_EXCLUDES = r"/(\.direnv|\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|venv|\.svn|_build|buck-out|build|dist)/"  # noqa: B950
try:
    import IPython  # noqa: F401
    import tokenize_rt  # noqa: F401
except ModuleNotFoundError:
    DEFAULT_INCLUDES = r"\.pyi?$"
else:
    DEFAULT_INCLUDES = r"(\.pyi?|\.ipynb)$"
STDIN_PLACEHOLDER = "__BLACK_STDIN_FILENAME__"
