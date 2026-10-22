"""Pickle loading restricted to the value types Black's caches contain.

Cache files can live inside a project checkout, so a crafted cache must never be
able to resolve an arbitrary global while it is being loaded.
"""

from __future__ import annotations

import io
import pickle
from typing import Any, BinaryIO

_SAFE_BUILTINS = frozenset({"bytearray", "complex", "frozenset", "set"})


class SafeUnpickler(pickle.Unpickler):
    """An unpickler that only resolves the builtin globals used by cache payloads."""

    def find_class(self, module: str, name: str) -> object:
        if module == "builtins" and name in _SAFE_BUILTINS:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(
            f"cache payload references disallowed global {module}.{name}"
        )


def load(stream: BinaryIO) -> Any:
    return SafeUnpickler(stream).load()


def loads(data: bytes) -> Any:
    return load(io.BytesIO(data))
