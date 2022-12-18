"""
Allows configuring optional test markers in config, see pyproject.toml.

Run optional tests with `pytest --run-optional=...`.

Mark tests to run only if an optional test ISN'T selected by prepending the mark with
"no_".

You can specify a "no_" prefix straight in config, in which case you can mark tests
to run when this tests ISN'T selected by omitting the "no_" prefix.

Specifying the name of the default behavior in `--run-optional=` is harmless.

Adapted from https://pypi.org/project/pytest-optional-tests/, (c) 2019 Reece Hart
"""

import itertools
import logging
import re
from functools import lru_cache
from typing import TYPE_CHECKING, FrozenSet, List, Set

import pytest

try:
    from pytest import StashKey
except ImportError:
    # pytest < 7
    from _pytest.store import StoreKey as StashKey  # type: ignore[no-redef]

log = logging.getLogger(__name__)


if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.config.argparsing import Parser
    from _pytest.mark.structures import MarkDecorator
    from _pytest.nodes import Node


ALL_POSSIBLE_OPTIONAL_MARKERS = StashKey[FrozenSet[str]]()
ENABLED_OPTIONAL_MARKERS = StashKey[FrozenSet[str]]()


def pytest_addoption(parser: "Parser") -> None:
    group = parser.getgroup("collect")
    group.addoption(
        "--run-optional",
        action="append",
        dest="run_optional",
        default=None,
        help="Optional test markers to run; comma-separated",
    )
    parser.addini("optional-tests", "List of optional tests markers", "linelist")


def pytest_configure(config: "Config") -> None:
    """Optional tests are markers.

    Use the syntax in https://docs.pytest.org/en/stable/mark.html#registering-marks.
    """
    ot_ini = config.inicfg.get("optional-tests") or []
    ot_markers = set()
    ot_run: Set[str] = set()
    if isinstance(ot_ini, str):
        ot_ini = ot_ini.strip().split("\n")
    marker_re = re.compile(r"^\s*(?P<no>no_)?(?P<marker>\w+)(:\s*(?P<description>.*))?")
    for ot in ot_ini:
        m = marker_re.match(ot)
        if not m:
            raise ValueError(f"{ot!r} doesn't match pytest marker syntax")

        marker = (m.group("no") or "") + m.group("marker")
        description = m.group("description")
        config.addinivalue_line("markers", f"{marker}: {description}")
        config.addinivalue_line(
            "markers", f"{no(marker)}: run when `{marker}` not passed"
        )
        ot_markers.add(marker)

    # collect requested optional tests
    passed_args = config.getoption("run_optional")
    if passed_args:
        ot_run.update(itertools.chain.from_iterable(a.split(",") for a in passed_args))
    ot_run |= {no(excluded) for excluded in ot_markers - ot_run}
    ot_markers |= {no(m) for m in ot_markers}

    log.info("optional tests to run:", ot_run)
    unknown_tests = ot_run - ot_markers
    if unknown_tests:
        raise ValueError(f"Unknown optional tests wanted: {unknown_tests!r}")

    store = config._store
    store[ALL_POSSIBLE_OPTIONAL_MARKERS] = frozenset(ot_markers)
    store[ENABLED_OPTIONAL_MARKERS] = frozenset(ot_run)


def pytest_collection_modifyitems(config: "Config", items: "List[Node]") -> None:
    store = config._store
    all_possible_optional_markers = store[ALL_POSSIBLE_OPTIONAL_MARKERS]
    enabled_optional_markers = store[ENABLED_OPTIONAL_MARKERS]

    for item in items:
        all_markers_on_test = {m.name for m in item.iter_markers()}
        optional_markers_on_test = all_markers_on_test & all_possible_optional_markers
        if not optional_markers_on_test or (
            optional_markers_on_test & enabled_optional_markers
        ):
            continue
        log.info("skipping non-requested optional", item)
        item.add_marker(skip_mark(frozenset(optional_markers_on_test)))


@lru_cache()
def skip_mark(tests: FrozenSet[str]) -> "MarkDecorator":
    names = ", ".join(sorted(tests))
    return pytest.mark.skip(reason=f"Marked with disabled optional tests ({names})")


@lru_cache()
def no(name: str) -> str:
    if name.startswith("no_"):
        return name[len("no_") :]
    return "no_" + name
