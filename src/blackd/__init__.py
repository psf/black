import asyncio
import logging
from concurrent.futures import Executor, ProcessPoolExecutor
from datetime import datetime, timezone
from functools import cache, partial
from multiprocessing import freeze_support

try:
    from aiohttp import web
    from multidict import MultiMapping
    from .middlewares import cors
except ImportError as ie:
    raise ImportError(
        "aiohttp dependency is not installed. Please install black[d]"
    ) from None

import click
import black
from _black_version import version as __version__
from black.concurrency import maybe_install_uvloop

# Headers configuration
HEADERS = {
    'protocol_version': 'X-Protocol-Version',
    'line_length': 'X-Line-Length',
    'python_variant': 'X-Python-Variant',
    'skip_first_line': 'X-Skip-Source-First-Line',
    'skip_string_norm': 'X-Skip-String-Normalization',
    'skip_magic_comma': 'X-Skip-Magic-Trailing-Comma',
    'preview': 'X-Preview',
    'unstable': 'X-Unstable',
    'unstable_feature': 'X-Enable-Unstable-Feature',
    'fast_or_safe': 'X-Fast-Or-Safe',
    'diff': 'X-Diff',
    'version': 'X-Black-Version'
}

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
def executor() -> Executor:
    return ProcessPoolExecutor()

def make_app() -> web.Application:
    app = web.Application(middlewares=[cors(allow_headers=tuple(HEADERS.values()) + ("Content-Type",))])
    app.add_routes([web.post("/", partial(handle, executor=executor()))])
    return app

async def handle(request: web.Request, executor: Executor) -> web.Response:
    headers = {HEADERS['version']: __version__}
    try:
        if request.headers.get(HEADERS['protocol_version'], "1") != "1":
            return web.Response(status=501, text="Protocol version 1 only")

        mode = parse_mode(request.headers)
        content = await request.content.read()
        charset = request.charset or "utf8"
        source = content.decode(charset)

        # Handle first line skipping if needed
        header = ""
        if mode.skip_source_first_line:
            nl_pos = source.find('\n') + 1
            header, source = source[:nl_pos], source[nl_pos:]

        # Format the content
        formatted = await asyncio.get_event_loop().run_in_executor(
            executor,
            partial(black.format_file_contents, 
                   source,
                   fast=request.headers.get(HEADERS['fast_or_safe']) == "fast",
                   mode=mode)
        )

        # Handle CRLF and diff if needed
        if '\r\n' in source:
            formatted = formatted.replace('\n', '\r\n')
        
        formatted = header + formatted
        
        if request.headers.get(HEADERS['diff']):
            formatted = await asyncio.get_event_loop().run_in_executor(
                executor,
                partial(black.diff, source, formatted,
                        f"In\t{datetime.now(timezone.utc)}",
                        f"Out\t{datetime.now(timezone.utc)}")
            )

        return web.Response(content_type=request.content_type,
                          charset=charset,
                          headers=headers,
                          text=formatted)
                          
    except black.NothingChanged:
        return web.Response(status=204, headers=headers)
    except black.InvalidInput as e:
        return web.Response(status=400, headers=headers, text=str(e))
    except Exception as e:
        logging.exception("Request handling error")
        return web.Response(status=500, headers=headers, text=str(e))

def parse_mode(headers: MultiMapping[str]) -> black.Mode:
    try:
        line_length = int(headers.get(HEADERS['line_length'], black.DEFAULT_LINE_LENGTH))
    except ValueError:
        raise HeaderError("Invalid line length header value") from None

    if HEADERS['python_variant'] in headers:
        value = headers[HEADERS['python_variant']]
        try:
            pyi, versions = parse_python_variant_header(value)
        except InvalidVariantHeader as e:
            raise HeaderError(
                f"Invalid value for {HEADERS['python_variant']}: {e.args[0]}",
            ) from None
    else:
        pyi = False
        versions = set()

    skip_string_normalization = bool(
        headers.get(HEADERS['skip_string_norm'], False)
    )
    skip_magic_trailing_comma = bool(headers.get(HEADERS['skip_magic_comma'], False))
    skip_source_first_line = bool(headers.get(HEADERS['skip_first_line'], False))

    preview = bool(headers.get(HEADERS['preview'], False))
    unstable = bool(headers.get(HEADERS['unstable'], False))
    enable_features: set[black.Preview] = set()
    enable_unstable_features = headers.get(HEADERS['unstable_feature'], "").split(",")
    for piece in enable_unstable_features:
        piece = piece.strip()
        if piece:
            try:
                enable_features.add(black.Preview[piece])
            except KeyError:
                raise HeaderError(
                    f"Invalid value for {HEADERS['unstable_feature']}: {piece}",
                ) from None

    return black.FileMode(
        target_versions=versions,
        is_pyi=pyi,
        line_length=line_length,
        skip_source_first_line=skip_source_first_line,
        string_normalization=not skip_string_normalization,
        magic_trailing_comma=not skip_magic_trailing_comma,
        preview=preview,
        unstable=unstable,
        enabled_features=enable_features,
    )

def parse_python_variant_header(value: str) -> tuple[bool, set[black.TargetVersion]]:
    if value == "pyi":
        return True, set()
    else:
        versions = set()
        for version in value.split(","):
            if version.startswith("py"):
                version = version[len("py") :]
            if "." in version:
                major_str, *rest = version.split(".")
            else:
                major_str = version[0]
                rest = [version[1:]] if len(version) > 1 else []
            try:
                major = int(major_str)
                if major not in (2, 3):
                    raise InvalidVariantHeader("major version must be 2 or 3")
                if len(rest) > 0:
                    minor = int(rest[0])
                    if major == 2:
                        raise InvalidVariantHeader("Python 2 is not supported")
                else:
                    # Default to lowest supported minor version.
                    minor = 7 if major == 2 else 3
                version_str = f"PY{major}{minor}"
                if major == 3 and not hasattr(black.TargetVersion, version_str):
                    raise InvalidVariantHeader(f"3.{minor} is not supported")
                versions.add(black.TargetVersion[version_str])
            except (KeyError, ValueError):
                raise InvalidVariantHeader("expected e.g. '3.7', 'py3.5'") from None
        return False, versions

def patched_main() -> None:
    maybe_install_uvloop()
    freeze_support()
    main()

if __name__ == "__main__":
    patched_main()
