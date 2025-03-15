import io
import json
import re
import sys
import tokenize
import traceback
from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime, timezone
from enum import Enum
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any, Optional, Union

import click
from mypy_extensions import mypyc_attr

from _black_version import version as __version__
from black.cache import Cache
from black.comments import normalize_fmt_off
from black.const import DEFAULT_LINE_LENGTH, STDIN_PLACEHOLDER
from black.files import find_project_root, get_gitignore, path_is_excluded
from black.handle_ipynb_magics import (
    jupyter_dependencies_are_installed,
    mask_cell,
    unmask_cell,
    validate_cell,
)
from black.linegen import LineGenerator
from black.lines import EmptyLineTracker, LinesBlock
from black.mode import Mode, Preview
from black.nodes import syms
from black.output import color_diff, diff, err, out
from black.parsing import ASTSafetyError, lib2to3_parse, parse_ast
from black.report import Changed, NothingChanged, Report

COMPILED = Path(__file__).suffix in (".pyd", ".so")

class WriteBack(Enum):
    NO = 0
    YES = 1
    DIFF = 2
    CHECK = 3
    COLOR_DIFF = 4

    @classmethod
    def from_configuration(cls, *, check: bool, diff: bool, color: bool = False) -> "WriteBack":
        if check and not diff:
            return cls.CHECK
        if diff and color:
            return cls.COLOR_DIFF
        return cls.DIFF if diff else cls.YES

FileMode = Mode

def format_str(src_contents: str, *, mode: Mode) -> str:
    src_node = lib2to3_parse(src_contents.lstrip(), mode.target_versions)
    dst_blocks = []
    line_generator = LineGenerator(mode=mode)
    elt = EmptyLineTracker(mode=mode)

    for current_line in line_generator.visit(src_node):
        block = elt.maybe_empty_lines(current_line)
        dst_blocks.append(block)
        block.content_lines.append(str(current_line))

    if dst_blocks:
        dst_blocks[-1].after = 0

    dst_contents = []
    for block in dst_blocks:
        dst_contents.extend(block.all_lines())

    return "".join(dst_contents) if dst_contents else ""

def format_file_contents(src_contents: str, *, mode: Mode) -> str:
    if mode.is_ipynb:
        return format_ipynb_string(src_contents, mode=mode)
    dst_contents = format_str(src_contents, mode=mode)
    if src_contents == dst_contents:
        raise NothingChanged
    return dst_contents

def format_ipynb_string(src_contents: str, *, mode: Mode) -> str:
    if not src_contents:
        raise NothingChanged

    nb = json.loads(src_contents)
    if nb.get("metadata", {}).get("language_info", {}).get("name") not in (None, "python"):
        raise NothingChanged

    modified = False
    for cell in nb["cells"]:
        if cell.get("cell_type") == "code":
            try:
                src = "".join(cell["source"])
                validate_cell(src, mode)
                masked_src, replacements = mask_cell(src)
                dst = format_str(masked_src, mode=mode)
                cell["source"] = unmask_cell(dst, replacements).splitlines(keepends=True)
                modified = True
            except:
                continue

    if modified:
        return json.dumps(nb, indent=1, ensure_ascii=False)
    raise NothingChanged

@click.command()
@click.option("-c", "--code", type=str, help="Format the code passed in as a string.")
@click.option("-l", "--line-length", type=int, default=DEFAULT_LINE_LENGTH)
@click.option("--check", is_flag=True)
@click.option("--diff", is_flag=True)
@click.option("--color/--no-color", is_flag=True)
@click.option("-q", "--quiet", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
@click.pass_context
def main(ctx, code, line_length, check, diff, color, quiet, verbose):
    ctx.ensure_object(dict)
    write_back = WriteBack.from_configuration(check=check, diff=diff, color=color)
    mode = Mode(line_length=line_length)
    report = Report(check=check, diff=diff, quiet=quiet, verbose=verbose)

    try:
        if code is not None:
            format_str(code, mode=mode)
        else:
            err("Code input is required")
            ctx.exit(1)
    except Exception as exc:
        if report.verbose:
            traceback.print_exc()
        report.failed(Path("<string>"), str(exc))

    if verbose or not quiet:
        out("All done! ✨ 🍰 ✨" if not report.return_code else "Oh no! 💥 💔 💥")
    ctx.exit(report.return_code)

if __name__ == "__main__":
    main()
