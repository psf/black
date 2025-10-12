import gc
import re
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from tests.util import DETERMINISTIC_HEADER, read_data

try:
    from aiohttp import web
    from aiohttp.test_utils import AioHTTPTestCase

    import blackd
    import blackd.client
except ImportError as e:
    raise RuntimeError("Please install Black with the 'd' extra") from e

import black


@pytest.mark.blackd
class BlackDTestCase(AioHTTPTestCase):
    def tearDown(self) -> None:
        # Work around https://github.com/python/cpython/issues/124706
        gc.collect()
        super().tearDown()

    def test_blackd_main(self) -> None:
        with patch("blackd.web.run_app"):
            result = CliRunner().invoke(blackd.main, [])
            if result.exception is not None:
                raise result.exception
            self.assertEqual(result.exit_code, 0)

    async def get_application(self) -> web.Application:
        return blackd.make_app()

    async def test_blackd_request_needs_formatting(self) -> None:
        response = await self.client.post("/", data=b"print('hello world')")
        self.assertEqual(response.status, 200)
        self.assertEqual(response.charset, "utf8")
        self.assertEqual(await response.read(), b'print("hello world")\n')

    async def test_blackd_request_no_change(self) -> None:
        response = await self.client.post("/", data=b'print("hello world")\n')
        self.assertEqual(response.status, 204)
        self.assertEqual(await response.read(), b"")

    async def test_blackd_request_syntax_error(self) -> None:
        response = await self.client.post("/", data=b"what even ( is")
        self.assertEqual(response.status, 400)
        content = await response.text()
        self.assertTrue(
            content.startswith("Cannot parse"),
            msg=f"Expected error to start with 'Cannot parse', got {repr(content)}",
        )

    async def test_blackd_unsupported_version(self) -> None:
        response = await self.client.post(
            "/", data=b"what", headers={blackd.PROTOCOL_VERSION_HEADER: "2"}
        )
        self.assertEqual(response.status, 501)

    async def test_blackd_supported_version(self) -> None:
        response = await self.client.post(
            "/", data=b"what", headers={blackd.PROTOCOL_VERSION_HEADER: "1"}
        )
        self.assertEqual(response.status, 200)

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

    async def test_blackd_pyi(self) -> None:
        source, expected = read_data("cases", "stub.py")
        response = await self.client.post(
            "/", data=source, headers={blackd.PYTHON_VARIANT_HEADER: "pyi"}
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(await response.text(), expected)

    async def test_blackd_diff(self) -> None:
        diff_header = re.compile(
            r"(In|Out)\t\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d\.\d\d\d\d\d\d\+\d\d:\d\d"
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

    async def test_blackd_line_length(self) -> None:
        response = await self.client.post(
            "/", data=b'print("hello")\n', headers={blackd.LINE_LENGTH_HEADER: "7"}
        )
        self.assertEqual(response.status, 200)

    async def test_blackd_invalid_line_length(self) -> None:
        response = await self.client.post(
            "/",
            data=b'print("hello")\n',
            headers={blackd.LINE_LENGTH_HEADER: "NaN"},
        )
        self.assertEqual(response.status, 400)

    async def test_blackd_skip_first_source_line(self) -> None:
        invalid_first_line = b"Header will be skipped\r\ni = [1,2,3]\nj = [1,2,3]\n"
        expected_result = b"Header will be skipped\r\ni = [1, 2, 3]\nj = [1, 2, 3]\n"
        response = await self.client.post("/", data=invalid_first_line)
        self.assertEqual(response.status, 400)
        response = await self.client.post(
            "/",
            data=invalid_first_line,
            headers={blackd.SKIP_SOURCE_FIRST_LINE: "true"},
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(await response.read(), expected_result)

    async def test_blackd_preview(self) -> None:
        response = await self.client.post(
            "/", data=b'print("hello")\n', headers={blackd.PREVIEW: "true"}
        )
        self.assertEqual(response.status, 204)

    async def test_blackd_response_black_version_header(self) -> None:
        response = await self.client.post("/")
        self.assertIsNotNone(response.headers.get(blackd.BLACK_VERSION_HEADER))

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

    async def test_cors_headers_present(self) -> None:
        response = await self.client.post("/", headers={"Origin": "*"})
        self.assertIsNotNone(response.headers.get("Access-Control-Allow-Origin"))
        self.assertIsNotNone(response.headers.get("Access-Control-Expose-Headers"))

    async def test_preserves_line_endings(self) -> None:
        for data in (b"c\r\nc\r\n", b"l\nl\n"):
            # test preserved newlines when reformatted
            response = await self.client.post("/", data=data + b" ")
            self.assertEqual(await response.text(), data.decode())
            # test 204 when no change
            response = await self.client.post("/", data=data)
            self.assertEqual(response.status, 204)

    async def test_normalizes_line_endings(self) -> None:
        for data, expected in ((b"c\r\nc\n", "c\r\nc\r\n"), (b"l\nl\r\n", "l\nl\n")):
            response = await self.client.post("/", data=data)
            self.assertEqual(await response.text(), expected)
            self.assertEqual(response.status, 200)

    async def test_single_character(self) -> None:
        response = await self.client.post("/", data="1")
        self.assertEqual(await response.text(), "1\n")
        self.assertEqual(response.status, 200)


@pytest.mark.blackd
class BlackDClientTestCase(AioHTTPTestCase):
    def tearDown(self) -> None:
        # Work around https://github.com/python/cpython/issues/124706
        gc.collect()
        super().tearDown()

    async def get_application(self) -> web.Application:
        return blackd.make_app()

    async def test_unformatted_code(self) -> None:
        client = blackd.client.BlackDClient(self.client.make_url("/"))
        unformatted_code = "def hello(): print('Hello, World!')"
        expected = 'def hello():\n    print("Hello, World!")\n'
        formatted_code = await client.format_code(unformatted_code)

        self.assertEqual(formatted_code, expected)

    async def test_formatted_code(self) -> None:
        client = blackd.client.BlackDClient(self.client.make_url("/"))
        initial_code = 'def hello():\n    print("Hello, World!")\n'
        expected = 'def hello():\n    print("Hello, World!")\n'
        formatted_code = await client.format_code(initial_code)

        self.assertEqual(formatted_code, expected)

    async def test_line_length(self) -> None:
        client = blackd.client.BlackDClient(self.client.make_url("/"), line_length=10)
        unformatted_code = "def hello(): print('Hello, World!')"
        expected = 'def hello():\n    print(\n        "Hello, World!"\n    )\n'
        formatted_code = await client.format_code(unformatted_code)

        self.assertEqual(formatted_code, expected)

    async def test_skip_source_first_line(self) -> None:
        client = blackd.client.BlackDClient(
            self.client.make_url("/"), skip_source_first_line=True
        )
        invalid_first_line = "Header will be skipped\r\ni = [1,2,3]\nj = [1,2,3]\n"
        expected_result = "Header will be skipped\r\ni = [1, 2, 3]\nj = [1, 2, 3]\n"
        formatted_code = await client.format_code(invalid_first_line)

        self.assertEqual(formatted_code, expected_result)

    async def test_skip_string_normalization(self) -> None:
        client = blackd.client.BlackDClient(
            self.client.make_url("/"), skip_string_normalization=True
        )
        unformatted_code = "def hello(): print('Hello, World!')"
        expected = "def hello():\n    print('Hello, World!')\n"
        formatted_code = await client.format_code(unformatted_code)

        self.assertEqual(formatted_code, expected)

    async def test_skip_magic_trailing_comma(self) -> None:
        client = blackd.client.BlackDClient(
            self.client.make_url("/"), skip_magic_trailing_comma=True
        )
        unformatted_code = "def hello(): print('Hello, World!')"
        expected = 'def hello():\n    print("Hello, World!")\n'
        formatted_code = await client.format_code(unformatted_code)

        self.assertEqual(formatted_code, expected)

    async def test_preview(self) -> None:
        client = blackd.client.BlackDClient(self.client.make_url("/"), preview=True)
        unformatted_code = "def hello(): print('Hello, World!')"
        expected = 'def hello():\n    print("Hello, World!")\n'
        formatted_code = await client.format_code(unformatted_code)

        self.assertEqual(formatted_code, expected)

    async def test_fast(self) -> None:
        client = blackd.client.BlackDClient(self.client.make_url("/"), fast=True)
        unformatted_code = "def hello(): print('Hello, World!')"
        expected = 'def hello():\n    print("Hello, World!")\n'
        formatted_code = await client.format_code(unformatted_code)

        self.assertEqual(formatted_code, expected)

    async def test_python_variant(self) -> None:
        client = blackd.client.BlackDClient(
            self.client.make_url("/"), python_variant="3.6"
        )
        unformatted_code = "def hello(): print('Hello, World!')"
        expected = 'def hello():\n    print("Hello, World!")\n'
        formatted_code = await client.format_code(unformatted_code)

        self.assertEqual(formatted_code, expected)

    async def test_diff(self) -> None:
        diff_header = re.compile(
            r"(In|Out)\t\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d\.\d\d\d\d\d\d\+\d\d:\d\d"
        )

        client = blackd.client.BlackDClient(self.client.make_url("/"), diff=True)
        source, _ = read_data("miscellaneous", "blackd_diff")
        expected, _ = read_data("miscellaneous", "blackd_diff.diff")

        diff = await client.format_code(source)
        diff = diff_header.sub(DETERMINISTIC_HEADER, diff)

        self.assertEqual(diff, expected)

    async def test_syntax_error(self) -> None:
        client = blackd.client.BlackDClient(self.client.make_url("/"))
        with_syntax_error = "def hello(): a 'Hello, World!'"
        with self.assertRaises(black.InvalidInput):
            _ = await client.format_code(with_syntax_error)
