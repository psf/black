import json
from typing import IO, Any

import click

import black


def generate_schema_from_click(
    cmd: click.Command,
) -> dict[str, Any]:
    result = {}
    for param in cmd.params:
        if not isinstance(param, click.Option) or param.is_eager:
            continue
        assert param.name
        name = param.name.replace("_", "-")
        default = {"default": param.default} if param.default is not None else {}
        json_type: dict[str, Any]
        match param.type:
            case click.types.IntParamType():
                json_type = {"type": "integer"}
            case click.types.StringParamType() | click.types.Path():
                json_type = {"type": "string"}
            case click.types.Choice(choices=choices):
                json_type = {"enum": choices}
            case click.types.BoolParamType():
                json_type = {"type": "boolean"}
            case _:
                msg = f"{param.type!r} not a known type for {param}"
                raise TypeError(msg)

        if param.multiple:
            json_type = {"type": "array", "items": json_type}

        result[name] = {**default, **json_type, "description": param.help}
    return result


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--schemastore", is_flag=True, help="SchemaStore format")
@click.option("--outfile", type=click.File(mode="w"), help="Write to file")
def main(schemastore: bool, outfile: IO[str]) -> None:
    properties = generate_schema_from_click(black.main)
    del properties["line-ranges"]
    schema: dict[str, Any] = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": (
            "https://github.com/psf/black/blob/main/black/resources/black.schema.json"
        ),
        "$comment": "black table in pyproject.toml",
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
    }
    if schemastore:
        schema["$id"] = ("https://json.schemastore.org/partial-black.json",)
        schema["properties"]["enable-unstable-feature"]["items"] = {"type": "string"}

    print(json.dumps(schema, indent=2), file=outfile)


if __name__ == "__main__":
    main()
