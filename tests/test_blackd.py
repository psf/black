import re
import sys
from typing import TYPE_CHECKING, Any, Callable, TypeVar
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from tests.util import DETERMINISTIC_HEADER, read_data

LESS_THAN_311 = sys.version_info < (3, 11)

if LESS_THAN_311:  # noqa: C901
    try:
        from aiohttp import web
        from aiohttp.test_utils import AioHTTPTestCase

        import blackd
    except ImportError as e:
        raise RuntimeError("Please install Black with the 'd' extra") from e

    if TYPE_CHECKING:
        F = TypeVar("F", bound=Callable[..., Any])

        unittest_run_loop: Callable[[F], F] = lambda x: x
    else:
        try:
            from aiohttp.test_utils import unittest_run_loop
        except ImportError:
            # unittest_run_loop is unnecessary and a no-op since aiohttp 3.8, and
            # aiohttp 4 removed it. To maintain compatibility we can make our own
            # no-op decorator.
            def unittest_run_loop(func, *args, **kwargs):
                return func

    @pytest.mark.blackd
    class BlackDTestCase(AioHTTPTestCase):  # type: ignore[misc]
        def test_blackd_main(self) -> None:
            with patch("blackd.web.run_app"):
                result = CliRunner().invoke(blackd.main, [])
                if result.exception is not None:
                    raise result.exception
                self.assertEqual(result.exit_code, 0)

        async def get_application(self) -> web.Application:
            return blackd.make_app()

        @unittest_run_loop
        async def test_blackd_request_needs_formatting(self) -> None:
            response = await self.client.post("/", data=b"print('hello world')")
            self.assertEqual(response.status, 200)
            self.assertEqual(response.charset, "utf8")
            self.assertEqual(await response.read(), b'print("hello world")\n')

        @unittest_run_loop
        async def test_blackd_request_no_change(self) -> None:
            response = await self.client.post("/", data=b'print("hello world")\n')
            self.assertEqual(response.status, 204)
            self.assertEqual(await response.read(), b"")

        @unittest_run_loop
        async def test_blackd_request_syntax_error(self) -> None:
            response = await self.client.post("/", data=b"what even ( is")
            self.assertEqual(response.status, 400)
            content = await response.text()
            self.assertTrue(
                content.startswith("Cannot parse"),
                msg=f"Expected error to start with 'Cannot parse', got {repr(content)}",
            )

        @unittest_run_loop
        async def test_blackd_unsupported_version(self) -> None:
            response = await self.client.post(
                "/", data=b"what", headers={blackd.PROTOCOL_VERSION_HEADER: "2"}
            )
            self.assertEqual(response.status, 501)

        @unittest_run_loop
        async def test_blackd_supported_version(self) -> None:
            response = await self.client.post(
                "/", data=b"what", headers={blackd.PROTOCOL_VERSION_HEADER: "1"}
            )
            self.assertEqual(response.status, 200)

        @unittest_run_loop
        async def test_blackd_invalid_python_variant(self) -> None:
            async def check(header_value: str, expected_status: int = 400) -> None:
                response = await self.client.post(
                    "/",
                    data=b"what",
                    headers={blackd.PYTHON_VARIANT_HEADER: header_value},
                )
                self.assertEqual(response.status, expected_status)

            await check("lol")
            await check("ruby3.5")
            await check("pyi3.6")
            await check("py1.5")
            await check("2")
            await check("2.7")
            await check("py2.7")
            await check("2.8")
            await check("py2.8")
            await check("3.0")
            await check("pypy3.0")
            await check("jython3.4")

        @unittest_run_loop
        async def test_blackd_pyi(self) -> None:
            source, expected = read_data("miscellaneous", "stub.pyi")
            response = await self.client.post(
                "/", data=source, headers={blackd.PYTHON_VARIANT_HEADER: "pyi"}
            )
            self.assertEqual(response.status, 200)
            self.assertEqual(await response.text(), expected)

        @unittest_run_loop
        async def test_blackd_diff(self) -> None:
            diff_header = re.compile(
                r"(In|Out)\t\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d\.\d\d\d\d\d\d \+\d\d\d\d"
            )

            source, _ = read_data("miscellaneous", "blackd_diff")
            expected, _ = read_data("miscellaneous", "blackd_diff.diff")

            response = await self.client.post(
                "/", data=source, headers={blackd.DIFF_HEADER: "true"}
            )
            self.assertEqual(response.status, 200)

            actual = await response.text()
            actual = diff_header.sub(DETERMINISTIC_HEADER, actual)
            self.assertEqual(actual, expected)

        @unittest_run_loop
        async def test_blackd_python_variant(self) -> None:
            code = (
                "def f(\n"
                "    and_has_a_bunch_of,\n"
                "    very_long_arguments_too,\n"
                "    and_lots_of_them_as_well_lol,\n"
                "    **and_very_long_keyword_arguments\n"
                "):\n"
                "    pass\n"
            )

            async def check(header_value: str, expected_status: int) -> None:
                response = await self.client.post(
                    "/", data=code, headers={blackd.PYTHON_VARIANT_HEADER: header_value}
                )
                self.assertEqual(
                    response.status, expected_status, msg=await response.text()
                )

            await check("3.6", 200)
            await check("py3.6", 200)
            await check("3.6,3.7", 200)
            await check("3.6,py3.7", 200)
            await check("py36,py37", 200)
            await check("36", 200)
            await check("3.6.4", 200)
            await check("3.4", 204)
            await check("py3.4", 204)
            await check("py34,py36", 204)
            await check("34", 204)

        @unittest_run_loop
        async def test_blackd_line_length(self) -> None:
            response = await self.client.post(
                "/", data=b'print("hello")\n', headers={blackd.LINE_LENGTH_HEADER: "7"}
            )
            self.assertEqual(response.status, 200)

        @unittest_run_loop
        async def test_blackd_invalid_line_length(self) -> None:
            response = await self.client.post(
                "/",
                data=b'print("hello")\n',
                headers={blackd.LINE_LENGTH_HEADER: "NaN"},
            )
            self.assertEqual(response.status, 400)

        @unittest_run_loop
        async def test_blackd_preview(self) -> None:
            response = await self.client.post(
                "/", data=b'print("hello")\n', headers={blackd.PREVIEW: "true"}
            )
            self.assertEqual(response.status, 204)

        @unittest_run_loop
        async def test_blackd_response_black_version_header(self) -> None:
            response = await self.client.post("/")
            self.assertIsNotNone(response.headers.get(blackd.BLACK_VERSION_HEADER))

        @unittest_run_loop
        async def test_cors_preflight(self) -> None:
            response = await self.client.options(
                "/",
                headers={
                    "Access-Control-Request-Method": "POST",
                    "Origin": "*",
                    "Access-Control-Request-Headers": "Content-Type",
                },
            )
            self.assertEqual(response.status, 200)
            self.assertIsNotNone(response.headers.get("Access-Control-Allow-Origin"))
            self.assertIsNotNone(response.headers.get("Access-Control-Allow-Headers"))
            self.assertIsNotNone(response.headers.get("Access-Control-Allow-Methods"))

        @unittest_run_loop
        async def test_cors_headers_present(self) -> None:
            response = await self.client.post("/", headers={"Origin": "*"})
            self.assertIsNotNone(response.headers.get("Access-Control-Allow-Origin"))
            self.assertIsNotNone(response.headers.get("Access-Control-Expose-Headers"))
