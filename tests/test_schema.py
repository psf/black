import importlib.metadata


def test_schema_entrypoint() -> None:
    (black_ep,) = importlib.metadata.entry_points(
        group="validate_pyproject.tool_schema", name="black"
    )

    black_fn = black_ep.load()
    schema = black_fn()
    assert schema == black_fn("black")
    assert schema["properties"]["line-length"]["type"] == "integer"
