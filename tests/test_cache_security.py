"""Cache files are data, so loading one must not execute attacker-chosen globals."""

from __future__ import annotations

import pickle
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from black.cache import Cache, get_cache_file
from black.mode import Mode
from blib2to3.pgen2 import grammar, safe_pickle


class _Payload:
    def __init__(self, marker: Path) -> None:
        self.marker = marker

    def __reduce__(self) -> tuple[Any, tuple[Any, ...]]:
        code = (
            "from pathlib import Path; "
            f"Path({str(self.marker)!r}).write_text('pwned')"
        )
        return subprocess.run, ([sys.executable, "-c", code],)


def _malicious_pickle(marker: Path) -> bytes:
    return pickle.dumps({"cache": _Payload(marker)})


def test_metadata_cache_rejects_unsafe_pickle(tmp_path: Path) -> None:
    marker = tmp_path / "pwned"
    get_cache_file(Mode(), tmp_path).write_bytes(_malicious_pickle(marker))

    cache = Cache.read(Mode(), tmp_path)

    assert cache.file_data == {}
    assert not marker.exists()


def test_grammar_cache_rejects_unsafe_pickle(tmp_path: Path) -> None:
    marker = tmp_path / "pwned"
    cache_file = tmp_path / "grammar.pickle"
    cache_file.write_bytes(_malicious_pickle(marker))

    with pytest.raises(pickle.UnpicklingError):
        grammar.Grammar().load(cache_file)

    assert not marker.exists()


def test_safe_unpickler_allows_collection_types() -> None:
    payload = {"set": {1, 2}, "frozenset": frozenset({3})}

    assert safe_pickle.loads(pickle.dumps(payload)) == payload


def test_normal_metadata_cache_still_round_trips(tmp_path: Path) -> None:
    source = tmp_path / "example.py"
    source.write_text("x = 1\n", encoding="utf-8")
    mode = Mode()
    Cache(mode, get_cache_file(mode, tmp_path)).write([source])

    cache = Cache.read(mode, tmp_path)

    assert str(source.resolve()) in cache.file_data


def test_normal_grammar_cache_still_round_trips(tmp_path: Path) -> None:
    original = grammar.Grammar()
    original.symbol2number = {"file_input": 256}
    original.number2symbol = {256: "file_input"}
    cache_file = tmp_path / "grammar.pickle"
    original.dump(cache_file)

    loaded = grammar.Grammar()
    loaded.load(cache_file)

    assert loaded.symbol2number == original.symbol2number
    assert loaded.number2symbol == original.number2symbol
