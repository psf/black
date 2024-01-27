import importlib.resources
import json
import sys
from typing import Any


def get_schema(tool_name: str = "cibuildwheel") -> Any:
    "Get the stored complete schema for black's settings."
    assert tool_name == "black", "Only black is supported."

    loc = "resources/black.schema.json"

    if sys.version_info < (3, 9):
        with importlib.resources.open_text("black", loc, encoding="utf-8") as f:
            return json.load(f)

    schema = importlib.resources.files("black").joinpath(loc)  # type: ignore[unreachable]
    with schema.open(encoding="utf-8") as f:
        return json.load(f)
