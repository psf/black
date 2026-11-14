import asyncio
import io
import socket
import subprocess
import sys
import threading
from collections.abc import Iterator
from pathlib import Path

import pytest

import blackd_client
from tests.util import PROJECT_ROOT

UNFORMATTED = "print('hello')\n"
FORMATTED = 'print("hello")\n'


def test_imports_only_stdlib() -> None:
    code = (
        "import sys, blackd_client\n"
        "print(sorted(m for m in ('black', 'blackd', 'aiohttp', 'click')"
        " if m in sys.modules))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
        cwd=PROJECT_ROOT,
        env={"PYTHONPATH": str(PROJECT_ROOT / "src")},
    )
    assert result.stdout.strip() == "[]"


def test_build_headers() -> None:
    args = blackd_client.parse_args([
        "-l",
        "100",
        "-t",
        "py311",
        "-t",
        "py312",
        "-S",
        "-C",
        "--skip-source-first-line",
        "--preview",
        "--unstable",
        "--enable-unstable-feature",
        "hug_parens_with_braces_and_square_brackets",
        "--fast",
        "f.py",
    ])
    assert blackd_client.build_headers(args) == {
        "X-Protocol-Version": "1",
        "X-Line-Length": "100",
        "X-Python-Variant": "py311,py312",
        "X-Skip-Source-First-Line": "yes",
        "X-Skip-String-Normalization": "yes",
        "X-Skip-Magic-Trailing-Comma": "yes",
        "X-Preview": "yes",
        "X-Unstable": "yes",
        "X-Enable-Unstable-Feature": "hug_parens_with_braces_and_square_brackets",
        "X-Fast-Or-Safe": "fast",
    }


def test_build_headers_defaults() -> None:
    args = blackd_client.parse_args(["f.py"])
    assert blackd_client.build_headers(args) == {"X-Protocol-Version": "1"}


def test_build_headers_pyi() -> None:
    args = blackd_client.parse_args(["--pyi", "f.pyi"])
    assert blackd_client.build_headers(args)["X-Python-Variant"] == "pyi"


@pytest.mark.parametrize(
    "argv",
    [
        ["--pyi", "-t", "py312", "f.py"],
        ["--fast", "--safe", "f.py"],
        ["-t", "3.12", "f.py"],
        ["--workers", "0", "f.py"],
        ["-", "-"],
    ],
)
def test_invalid_arguments(argv: list[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        blackd_client.parse_args(argv)
    assert exc.value.code == 2


def test_unreachable_server(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    src = tmp_path / "a.py"
    src.write_text(UNFORMATTED, encoding="utf-8")

    code = blackd_client.main([f"--url=http://127.0.0.1:{port}", str(src)])

    assert code == 123
    assert "cannot reach blackd" in capsys.readouterr().err
    assert src.read_text(encoding="utf-8") == UNFORMATTED


def test_directory_is_rejected(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = blackd_client.main(["--url=http://127.0.0.1:1", str(tmp_path)])
    assert code == 123
    assert "is a directory" in capsys.readouterr().err


@pytest.fixture(scope="module")
def blackd_url() -> Iterator[str]:
    try:
        from aiohttp import web

        import blackd
    except ImportError:
        pytest.skip("needs the 'd' extra")

    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    loop = asyncio.new_event_loop()
    runner = web.AppRunner(blackd.make_app())
    loop.run_until_complete(runner.setup())
    loop.run_until_complete(web.SockSite(runner, sock).start())
    thread = threading.Thread(target=loop.run_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        loop.call_soon_threadsafe(loop.stop)
        thread.join()
        loop.run_until_complete(runner.cleanup())
        loop.close()
        sock.close()


@pytest.mark.blackd
def test_formats_files_in_place(
    blackd_url: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    changed = tmp_path / "changed.py"
    changed.write_text(UNFORMATTED, encoding="utf-8")
    unchanged = tmp_path / "unchanged.py"
    unchanged.write_text(FORMATTED, encoding="utf-8")

    code = blackd_client.main([f"--url={blackd_url}", str(changed), str(unchanged)])

    assert code == 0
    assert changed.read_text(encoding="utf-8") == FORMATTED
    assert unchanged.read_text(encoding="utf-8") == FORMATTED
    err = capsys.readouterr().err
    assert f"reformatted {changed}" in err
    assert "1 file reformatted, 1 file left unchanged." in err


@pytest.mark.blackd
def test_check(
    blackd_url: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    src = tmp_path / "a.py"
    src.write_text(UNFORMATTED, encoding="utf-8")

    code = blackd_client.main([f"--url={blackd_url}", "--check", str(src)])

    assert code == 1
    assert src.read_text(encoding="utf-8") == UNFORMATTED
    captured = capsys.readouterr()
    assert captured.out == ""
    assert f"would reformat {src}" in captured.err
    assert "1 file would be reformatted." in captured.err


@pytest.mark.blackd
def test_check_unchanged(blackd_url: str, tmp_path: Path) -> None:
    src = tmp_path / "a.py"
    src.write_text(FORMATTED, encoding="utf-8")
    assert blackd_client.main([f"--url={blackd_url}", "--check", str(src)]) == 0


@pytest.mark.blackd
def test_diff(
    blackd_url: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    src = tmp_path / "a.py"
    src.write_text(UNFORMATTED, encoding="utf-8")

    code = blackd_client.main([f"--url={blackd_url}", "--diff", str(src)])

    assert code == 0
    assert src.read_text(encoding="utf-8") == UNFORMATTED
    out = capsys.readouterr().out
    assert out.startswith(f"--- {src}\t")
    assert f"\n+++ {src}\t" in out
    assert "\n-print('hello')\n+print(\"hello\")\n" in out


@pytest.mark.blackd
def test_stdin(
    blackd_url: str,
    monkeypatch: pytest.MonkeyPatch,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    stdin = io.TextIOWrapper(io.BytesIO(UNFORMATTED.encode()), encoding="utf-8")
    monkeypatch.setattr(sys, "stdin", stdin)

    code = blackd_client.main([f"--url={blackd_url}", "-q", "-"])

    assert code == 0
    assert capsysbinary.readouterr().out == FORMATTED.encode()


@pytest.mark.blackd
def test_options_reach_blackd(blackd_url: str, tmp_path: Path) -> None:
    src = tmp_path / "a.py"
    src.write_text("x = [1, 2, 3]\n", encoding="utf-8")
    quotes = tmp_path / "b.py"
    quotes.write_text("y = 'a'\n", encoding="utf-8")

    code = blackd_client.main(
        [f"--url={blackd_url}", "-l", "10", "-S", str(src), str(quotes)]
    )

    assert code == 0
    assert src.read_text(encoding="utf-8") == "x = [\n    1,\n    2,\n    3,\n]\n"
    assert quotes.read_text(encoding="utf-8") == "y = 'a'\n"


@pytest.mark.blackd
def test_syntax_error_does_not_stop_other_files(
    blackd_url: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text("def f(:\n", encoding="utf-8")
    good = tmp_path / "good.py"
    good.write_text(UNFORMATTED, encoding="utf-8")

    code = blackd_client.main([f"--url={blackd_url}", str(bad), str(good)])

    assert code == 123
    assert good.read_text(encoding="utf-8") == FORMATTED
    err = capsys.readouterr().err
    assert f"error: cannot format {bad}: cannot parse: 1:6" in err
    assert "1 file reformatted, 1 file failed to reformat." in err


@pytest.mark.blackd
def test_many_files(blackd_url: str, tmp_path: Path) -> None:
    srcs = []
    for i in range(25):
        src = tmp_path / f"f{i}.py"
        src.write_text(f"x = {{  'a':{i}  }}\n", encoding="utf-8")
        srcs.append(src)

    code = blackd_client.main([f"--url={blackd_url}", "-q", "-W", "4", *map(str, srcs)])

    assert code == 0
    for i, src in enumerate(srcs):
        assert src.read_text(encoding="utf-8") == f'x = {{"a": {i}}}\n'


@pytest.mark.blackd
def test_keeps_source_encoding(blackd_url: str, tmp_path: Path) -> None:
    src = tmp_path / "a.py"
    src.write_bytes("# -*- coding: latin-1 -*-\nx = 'é'\n".encode("latin-1"))

    assert blackd_client.main([f"--url={blackd_url}", "-q", str(src)]) == 0
    assert src.read_bytes() == '# -*- coding: latin-1 -*-\nx = "é"\n'.encode("latin-1")
