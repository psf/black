import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import List, Tuple, Iterator

THIS_DIR = Path(__file__).parent
PROJECT_ROOT = THIS_DIR.parent
EMPTY_LINE = "# EMPTY LINE WITH WHITESPACE" + " (this comment will be removed)"
DETERMINISTIC_HEADER = "[Deterministic header]"


@contextmanager
def skip_if_exception(e: str) -> Iterator[None]:
    try:
        yield
    except Exception as exc:
        if exc.__class__.__name__ == e:
            unittest.skip(f"Encountered expected exception {exc}, skipping")
        else:
            raise


def read_data(name: str, data: bool = True) -> Tuple[str, str]:
    """read_data('test_name') -> 'input', 'output'"""
    if not name.endswith((".py", ".pyi", ".out", ".diff")):
        name += ".py"
    _input: List[str] = []
    _output: List[str] = []
    base_dir = THIS_DIR / "data" if data else PROJECT_ROOT
    with open(base_dir / name, "r", encoding="utf8") as test:
        lines = test.readlines()
    result = _input
    for line in lines:
        line = line.replace(EMPTY_LINE, "")
        if line.rstrip() == "# output":
            result = _output
            continue

        result.append(line)
    if _input and not _output:
        # If there's no output marker, treat the entire file as already pre-formatted.
        _output = _input[:]
    return "".join(_input).strip() + "\n", "".join(_output).strip() + "\n"
