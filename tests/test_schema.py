import importlib.metadata
import sys


def test_schema_entrypoint() -> None:
    if sys.version_info < (3, 10):
        eps = importlib.metadata.entry_points()["validate_pyproject.tool_schema"]
        (black_ep,) = [ep for ep in eps if ep.name == "black"]
    else:
        (black_ep,) = importlib.metadata.entry_points(
            group="validate_pyproject.tool_schema", name="black"
        )

    black_fn = black_ep.load()
    schema = black_fn()
    assert schema == black_fn("black")
    assert schema["properties"]["line-length"]["type"] == "integer"
