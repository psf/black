import asyncio
from concurrent.futures import Executor, ProcessPoolExecutor
from functools import partial
import logging
from typing import Set

from aiohttp import web
import black
import click

# This is used internally by tests to shut down the server prematurely
_stop_signal = asyncio.Event()

VERSION_HEADER = "X-Protocol-Version"
LINE_LENGTH_HEADER = "X-Line-Length"
PYTHON_VARIANT_HEADER = "X-Python-Variant"
SKIP_STRING_NORMALIZATION_HEADER = "X-Skip-String-Normalization"
SKIP_NUMERIC_UNDERSCORE_NORMALIZATION_HEADER = "X-Skip-Numeric-Underscore-Normalization"
FAST_OR_SAFE_HEADER = "X-Fast-Or-Safe"


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--bind-host", type=str, help="Address to bind the server to.", default="localhost"
)
@click.option("--bind-port", type=int, help="Port to listen on", default=45484)
@click.version_option(version=black.__version__)
def main(bind_host: str, bind_port: int) -> None:
    logging.basicConfig(level=logging.INFO)
    app = make_app()
    ver = black.__version__
    black.out(f"blackd version {ver} listening on {bind_host} port {bind_port}")
    web.run_app(app, host=bind_host, port=bind_port, handle_signals=True, print=None)


def make_app() -> web.Application:
    app = web.Application()
    executor = ProcessPoolExecutor()
    app.add_routes([web.post("/", partial(handle, executor=executor))])
    return app


async def handle(request: web.Request, executor: Executor) -> web.Response:
    try:
        if request.headers.get(VERSION_HEADER, "1") != "1":
            return web.Response(
                status=501, text="This server only supports protocol version 1"
            )
        try:
            line_length = int(
                request.headers.get(LINE_LENGTH_HEADER, black.DEFAULT_LINE_LENGTH)
            )
        except ValueError:
            return web.Response(status=400, text="Invalid line length header value")
        pyi = False
        versions: Set[black.TargetVersion] = set()
        if PYTHON_VARIANT_HEADER in request.headers:
            value = request.headers[PYTHON_VARIANT_HEADER]
            if value == "pyi":
                pyi = True
            else:
                for version in value.split(","):
                    tag = "cpy"
                    if version.startswith("cpy"):
                        version = version[len("cpy") :]
                    elif version.startswith("pypy"):
                        tag = "pypy"
                        version = version[len("pypy") :]
                    major_str, *rest = version.split(".")
                    try:
                        major = int(major_str)
                        if len(rest) > 0:
                            minor = int(rest[0])
                        else:
                            # Default to lowest supported minor version.
                            minor = 7 if major == 2 else 3
                        version_str = f"{tag.upper()}{major}{minor}"
                        # If PyPY is the same as CPython in some version, use the corresponding
                        # CPython version.
                        if tag == "pypy" and not hasattr(
                            black.TargetVersion, version_str
                        ):
                            version_str = f"CPY{major}{minor}"
                        versions.add(black.TargetVersion[version_str])
                    except (KeyError, ValueError):
                        return web.Response(
                            status=400,
                            text=f"Invalid value for {PYTHON_VARIANT_HEADER}",
                        )

        skip_string_normalization = bool(
            request.headers.get(SKIP_STRING_NORMALIZATION_HEADER, False)
        )
        skip_numeric_underscore_normalization = bool(
            request.headers.get(SKIP_NUMERIC_UNDERSCORE_NORMALIZATION_HEADER, False)
        )
        fast = False
        if request.headers.get(FAST_OR_SAFE_HEADER, "safe") == "fast":
            fast = True
        mode = black.FileMode(
            target_versions=versions,
            is_pyi=pyi,
            line_length=line_length,
            string_normalization=not skip_string_normalization,
            numeric_underscore_normalization=not skip_numeric_underscore_normalization,
        )
        req_bytes = await request.content.read()
        charset = request.charset if request.charset is not None else "utf8"
        req_str = req_bytes.decode(charset)
        loop = asyncio.get_event_loop()
        formatted_str = await loop.run_in_executor(
            executor, partial(black.format_file_contents, req_str, fast=fast, mode=mode)
        )
        return web.Response(
            content_type=request.content_type, charset=charset, text=formatted_str
        )
    except black.NothingChanged:
        return web.Response(status=204)
    except black.InvalidInput as e:
        return web.Response(status=400, text=str(e))
    except Exception as e:
        logging.exception("Exception during handling a request")
        return web.Response(status=500, text=str(e))


def patched_main() -> None:
    black.patch_click()
    main()


if __name__ == "__main__":
    patched_main()
