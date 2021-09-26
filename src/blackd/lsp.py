from functools import partial
import asyncio
from json.decoder import JSONDecodeError
import os
from pathlib import Path
from aiohttp import web
from aiohttp_json_rpc import JsonRpc, RpcInvalidParamsError
from aiohttp_json_rpc.protocol import JsonRpcMsgTyp
from aiohttp_json_rpc.rpc import JsonRpcRequest
from concurrent.futures import Executor

from typing import Awaitable, Callable, Generator, List, Optional
from typing_extensions import TypedDict
from difflib import SequenceMatcher
from urllib.parse import urlparse
from urllib.request import url2pathname
import black

# Reference: https://bit.ly/2XScAZF
DocumentUri = str


class TextDocumentIdentifier(TypedDict):
    """"""

    uri: DocumentUri


class FormattingOptions(TypedDict):
    """Reference: https://bit.ly/3CPqmvk"""

    tabSize: int
    insertSpaces: bool
    trimTrailingWhitespace: Optional[bool]
    insertFinalNewline: Optional[bool]
    trimFinalNewlines: Optional[bool]


class DocumentFormattingParams(TypedDict):
    """Reference: https://bit.ly/3ibxWZk"""

    textDocument: TextDocumentIdentifier
    options: FormattingOptions


class Position(TypedDict):
    """Reference: https://bit.ly/3CQDNuX"""

    line: int
    character: int


class Range(TypedDict):
    """Reference: https://bit.ly/3zKxWp4"""

    start: Position
    end: Position


class TextEdit(TypedDict):
    """Reference: https://bit.ly/3AJCFsF"""

    range: Range
    newText: str


def make_lsp_handler(
    executor: Executor,
) -> Callable[[web.Request], Awaitable[web.Response]]:
    rpc = JsonRpc()

    async def formatting_handler(request: web.Request) -> web.Response:
        return await handle_formatting(executor, request)

    rpc.add_methods(
        ("", formatting_handler, "textDocument/formatting"),
    )
    return rpc.handle_request  # type: ignore


def uri_to_path(uri_str: str) -> Path:
    uri = urlparse(uri_str)
    if uri.scheme != "file":
        raise RpcInvalidParamsError(message="only file:// uri scheme is supported")
    return Path("{0}{0}{1}{0}".format(os.path.sep, uri.netloc)) / url2pathname(uri.path)


def format(src_path: os.PathLike) -> List[TextEdit]:
    def gen() -> Generator[TextEdit, None, None]:
        with open(src_path, "rb") as buf:
            src, encoding, newline = black.decode_bytes(buf.read())
        try:
            formatted_str = black.format_file_contents(
                src, fast=True, mode=black.Mode()
            )
        except black.NothingChanged:
            return
        except JSONDecodeError as e:
            raise RpcInvalidParamsError(
                message="File cannot be parsed as a Jupyter notebook"
            ) from e
        cmp = SequenceMatcher(a=src, b=formatted_str)
        for op, i1, i2, j1, j2 in cmp.get_opcodes():
            if op == "equal":
                continue

            rng = Range(start=offset_to_pos(i1, src), end=offset_to_pos(i2, src))

            if op in {"insert", "replace"}:
                yield TextEdit(range=rng, newText=formatted_str[j1:j2])
            elif op == "delete":
                yield TextEdit(range=rng, newText="")

    return list(gen())


def offset_to_pos(offset: int, src: str) -> Position:
    line = src.count("\n", 0, offset)
    last_nl = src.rfind("\n", 0, offset)
    character = offset if last_nl == -1 else offset - last_nl
    return Position(line=line, character=character)


async def handle_formatting(
    executor: Executor, request: JsonRpcRequest
) -> Optional[List[TextEdit]]:
    if request.msg.type != JsonRpcMsgTyp.REQUEST:
        raise RpcInvalidParamsError

    params: DocumentFormattingParams = request.msg.data["params"]
    path = uri_to_path(params["textDocument"]["uri"])
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, partial(format, path))
