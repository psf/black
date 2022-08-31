from typing import Awaitable, Callable, Iterable

from aiohttp.web_middlewares import middleware
from aiohttp.web_request import Request
from aiohttp.web_response import StreamResponse

Handler = Callable[[Request], Awaitable[StreamResponse]]
Middleware = Callable[[Request, Handler], Awaitable[StreamResponse]]


def cors(allow_headers: Iterable[str]) -> Middleware:
    @middleware  # type: ignore[misc]
    async def impl(request: Request, handler: Handler) -> StreamResponse:
        is_options = request.method == "OPTIONS"
        is_preflight = is_options and "Access-Control-Request-Method" in request.headers
        if is_preflight:
            resp = StreamResponse()
        else:
            resp = await handler(request)

        origin = request.headers.get("Origin")
        if not origin:
            return resp

        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Expose-Headers"] = "*"
        if is_options:
            resp.headers["Access-Control-Allow-Headers"] = ", ".join(allow_headers)
            resp.headers["Access-Control-Allow-Methods"] = ", ".join(
                ("OPTIONS", "POST")
            )

        return resp

    return impl  # type: ignore[no-any-return]
