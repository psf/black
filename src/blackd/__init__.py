import asyncio
import logging
from concurrent.futures import Executor, ProcessPoolExecutor
from datetime import datetime, timezone
from functools import cache, partial
from multiprocessing import freeze_support
from aiohttp import web
from multidict import MultiMapping
import click
import black
from _black_version import version as __version__
from black.concurrency import maybe_install_uvloop

_stop_signal = asyncio.Event()

PROTOCOL_VERSION_HEADER = "X-Protocol-Version"
LINE_LENGTH_HEADER = "X-Line-Length"
PYTHON_VARIANT_HEADER = "X-Python-Variant"
SKIP_SOURCE_FIRST_LINE = "X-Skip-Source-First-Line"
SKIP_STRING_NORMALIZATION_HEADER = "X-Skip-String-Normalization"
SKIP_MAGIC_TRAILING_COMMA = "X-Skip-Magic-Trailing-Comma"
PREVIEW = "X-Preview"
UNSTABLE = "X-Unstable"
ENABLE_UNSTABLE_FEATURE = "X-Enable-Unstable-Feature"
FAST_OR_SAFE_HEADER = "X-Fast-Or-Safe"
DIFF_HEADER = "X-Diff"

BLACK_HEADERS = [
    PROTOCOL_VERSION_HEADER, LINE_LENGTH_HEADER, PYTHON_VARIANT_HEADER,
    SKIP_SOURCE_FIRST_LINE, SKIP_STRING_NORMALIZATION_HEADER, SKIP_MAGIC_TRAILING_COMMA,
    PREVIEW, UNSTABLE, ENABLE_UNSTABLE_FEATURE, FAST_OR_SAFE_HEADER, DIFF_HEADER
]

BLACK_VERSION_HEADER = "X-Black-Version"

class HeaderError(Exception): pass
class InvalidVariantHeader(Exception): pass

@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--bind-host", type=str, default="localhost", show_default=True)
@click.option("--bind-port", type=int, default=45484, show_default=True)
@click.version_option(version=black.__version__)
def main(bind_host: str, bind_port: int) -> None:
    logging.basicConfig(level=logging.INFO)
    app = make_app()
    black.out(f"blackd version {black.__version__} listening on {bind_host} port {bind_port}")
    web.run_app(app, host=bind_host, port=bind_port, handle_signals=True, print=None)

@cache
def executor() -> Executor: return ProcessPoolExecutor()

def make_app() -> web.Application:
    app = web.Application(middlewares=[cors(allow_headers=(*BLACK_HEADERS, "Content-Type"))])
    app.add_routes([web.post("/", partial(handle, executor=executor()))])
    return app

async def handle(request: web.Request, executor: Executor) -> web.Response:
    headers = {BLACK_VERSION_HEADER: __version__}
    try:
        if request.headers.get(PROTOCOL_VERSION_HEADER, "1") != "1":
            return web.Response(status=501, text="This server only supports protocol version 1")

        fast = request.headers.get(FAST_OR_SAFE_HEADER, "safe") == "fast"
        try: mode = parse_mode(request.headers)
        except HeaderError as e: return web.Response(status=400, text=e.args[0])

        req_str = (await request.content.read()).decode(request.charset or "utf8")
        then = datetime.now(timezone.utc)

        if mode.skip_source_first_line:
            first_newline = req_str.find("\n") + 1
            header, req_str = req_str[:first_newline], req_str[first_newline:]

        formatted_str = await asyncio.get_event_loop().run_in_executor(
            executor, partial(black.format_file_contents, req_str, fast=fast, mode=mode)
        
        )

        if "\r\n" in req_str: 
            formatted_str = formatted_str.replace("\n", "\r\n")
        formatted_str = header + formatted_str

        if request.headers.get(DIFF_HEADER, False):
            formatted_str = await asyncio.get_event_loop().run_in_executor(
                executor, partial(black.diff, header + req_str, formatted_str, f"In\t{then}", f"Out\t{datetime.now(timezone.utc)}"))

        return web.Response(content_type=request.content_type, charset=request.charset or "utf8", headers=headers, text=formatted_str)
    except black.NothingChanged: return web.Response(status=204, headers=headers)
    except black.InvalidInput as e: return web.Response(status=400, headers=headers, text=str(e))
    except Exception as e:
        logging.exception("Exception during handling a request")
        return web.Response(status=500, headers=headers, text=str(e))

def parse_mode(headers: MultiMapping[str]) -> black.Mode:
    try: line_length = int(headers.get(LINE_LENGTH_HEADER, black.DEFAULT_LINE_LENGTH))
    except ValueError: raise HeaderError("Invalid line length header value")

    pyi, versions = (True, set()) if headers.get(PYTHON_VARIANT_HEADER) == "pyi" else (False, set())
    if PYTHON_VARIANT_HEADER in headers:
        try: pyi, versions = parse_python_variant_header(headers[PYTHON_VARIANT_HEADER])
        except InvalidVariantHeader as e: raise HeaderError(f"Invalid value for {PYTHON_VARIANT_HEADER}: {e.args[0]}")

    enable_features = {black.Preview[piece.strip()] for piece in headers.get(ENABLE_UNSTABLE_FEATURE, "").split(",") if piece.strip()}
    return black.FileMode(
        target_versions=versions, is_pyi=pyi, line_length=line_length,
        skip_source_first_line=bool(headers.get(SKIP_SOURCE_FIRST_LINE, False)),
        string_normalization=not bool(headers.get(SKIP_STRING_NORMALIZATION_HEADER, False)),
        magic_trailing_comma=not bool(headers.get(SKIP_MAGIC_TRAILING_COMMA, False)),
        preview=bool(headers.get(PREVIEW, False)), unstable=bool(headers.get(UNSTABLE, False)),
        enabled_features=enable_features
    )

def parse_python_variant_header(value: str) -> tuple[bool, set[black.TargetVersion]]:
    if value == "pyi": return True, set()
    versions = set()
    for version in value.split(","):
        version = version[2:] if version.startswith("py") else version
        major_str, *rest = version.split(".") if "." in version else (version[0], version[1:] if len(version) > 1 else [])
        try:
            major = int(major_str)
            if major not in (2, 3): raise InvalidVariantHeader("major version must be 2 or 3")
            if major == 2: raise InvalidVariantHeader("Python 2 is not supported")
            minor = int(rest[0]) if rest else 3
            version_str = f"PY{major}{minor}"
            if major == 3 and not hasattr(black.TargetVersion, version_str): raise InvalidVariantHeader(f"3.{minor} is not supported")
            versions.add(black.TargetVersion[version_str])
        except (KeyError, ValueError): raise InvalidVariantHeader("expected e.g. '3.7', 'py3.5'")
    return False, versions

def patched_main() -> None:
    maybe_install_uvloop()
    freeze_support()
    main()

if __name__ == "__main__":
    patched_main()
