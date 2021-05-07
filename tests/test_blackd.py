import re
from unittest.mock import patch

from click.testing import CliRunner
import pytest

from tests.util import read_data, DETERMINISTIC_HEADER

try:
    import blackd
    from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
    from aiohttp import web
except ImportError:
    has_blackd_deps = False
else:
    has_blackd_deps = True


@pytest.mark.blackd
class BlackDTestCase(AioHTTPTestCase):
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
                "/", data=b"what", headers={blackd.PYTHON_VARIANT_HEADER: header_value}
            )
            self.assertEqual(response.status, expected_status)

        await check("lol")
        await check("ruby3.5")
        await check("pyi3.6")
        await check("py1.5")
        await check("2.8")
        await check("py2.8")
        await check("3.0")
        await check("pypy3.0")
        await check("jython3.4")

    @unittest_run_loop
    async def test_blackd_pyi(self) -> None:
        source, expected = read_data("stub.pyi")
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

        source, _ = read_data("blackd_diff.py")
        expected, _ = read_data("blackd_diff.diff")

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

        await check("2", 204)
        await check("2.7", 204)
        await check("py2.7", 204)
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
            "/", data=b'print("hello")\n', headers={blackd.LINE_LENGTH_HEADER: "NaN"}
        )
        self.assertEqual(response.status, 400)

    @unittest_run_loop
    async def test_blackd_response_black_version_header(self) -> None:
        response = await self.client.post("/")
        self.assertIsNotNone(response.headers.get(blackd.BLACK_VERSION_HEADER))
