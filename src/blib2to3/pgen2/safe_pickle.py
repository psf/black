"""Restricted unpickling for Black's on-disk caches.

Cache files (the format cache in ``black.cache`` and the grammar tables in
``blib2to3.pgen2.grammar``) are plain data: dicts, lists, tuples, sets and
scalar values.  Deserializing them with an unrestricted ``pickle.load`` lets
a crafted file checked into a repository execute arbitrary code when Black
runs in that checkout (e.g. via a project-relative ``cache-dir``).

``RestrictedUnpickler`` only allows those basic container and scalar types;
anything else raises ``pickle.UnpicklingError``, which all cache readers
already treat as "cache miss".
"""

import builtins
import io
import pickle
from typing import Any

_SAFE_BUILTINS: frozenset[type] = frozenset({
    dict,
    list,
    tuple,
    set,
    frozenset,
    str,
    bytes,
    bytearray,
    int,
    float,
    bool,
    complex,
    type(None),
})


class RestrictedUnpickler(pickle.Unpickler):
    """Unpickler that only resolves explicitly allow-listed builtins."""

    def find_class(self, module: str, name: str) -> Any:
        if module == "builtins":
            cls = getattr(builtins, name, None)
            if cls in _SAFE_BUILTINS:
                return cls
        raise pickle.UnpicklingError(
            f"Blocked deserialization of {module}.{name}: "
            "cache files may only contain basic Python types"
        )


def safe_load(file: io.BufferedReader) -> Any:
    """Load pickled cache data, rejecting anything but basic Python types."""
    return RestrictedUnpickler(file).load()


def safe_loads(data: bytes) -> Any:
    """Load pickled cache data from bytes, rejecting non-basic types."""
    return RestrictedUnpickler(io.BytesIO(data)).load()
