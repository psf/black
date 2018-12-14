import asyncio
from concurrent.futures import Executor, ProcessPoolExecutor
from functools import partial
import logging
from multiprocessing import freeze_support

from aiohttp import web
import aiohttp_cors
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

BLACK_HEADERS = [
    VERSION_HEADER,
    LINE_LENGTH_HEADER,
    PYTHON_VARIANT_HEADER,
    SKIP_STRING_NORMALIZATION_HEADER,
    SKIP_NUMERIC_UNDERSCORE_NORMALIZATION_HEADER,
    FAST_OR_SAFE_HEADER,
]


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

    cors = aiohttp_cors.setup(app)
    resource = cors.add(app.router.add_resource("/"))
    cors.add(
        resource.add_route("POST", partial(handle, executor=executor)),
        {
            "*": aiohttp_cors.ResourceOptions(
                allow_headers=(*BLACK_HEADERS, "Content-Type"), expose_headers="*"
            )
        },
    )

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
        py36 = False
        pyi = False
        if PYTHON_VARIANT_HEADER in request.headers:
            value = request.headers[PYTHON_VARIANT_HEADER]
            if value == "pyi":
                pyi = True
            else:
                try:
                    major, *rest = value.split(".")
                    if int(major) == 3 and len(rest) > 0:
                        if int(rest[0]) >= 6:
                            py36 = True
                except ValueError:
                    return web.Response(
                        status=400, text=f"Invalid value for {PYTHON_VARIANT_HEADER}"
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
        mode = black.FileMode.from_configuration(
            py36=py36,
            pyi=pyi,
            skip_string_normalization=skip_string_normalization,
            skip_numeric_underscore_normalization=skip_numeric_underscore_normalization,
        )
        req_bytes = await request.content.read()
        charset = request.charset if request.charset is not None else "utf8"
        req_str = req_bytes.decode(charset)
        loop = asyncio.get_event_loop()
        formatted_str = await loop.run_in_executor(
            executor,
            partial(
                black.format_file_contents,
                req_str,
                line_length=line_length,
                fast=fast,
                mode=mode,
            ),
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
    freeze_support()
    black.patch_click()
    main()


if __name__ == "__main__":
    patched_main()
