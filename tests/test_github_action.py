import runpy
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ACTION_MAIN = Path(__file__).resolve().parents[1] / "action" / "main.py"
pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 11), reason="use_pyproject requires Python 3.11 or later"
)


@pytest.fixture
def action_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_ACTION_PATH", str(tmp_path))
    for name, value in {
        "INPUT_USE_PYPROJECT": "true",
        "INPUT_VERSION": "",
        "INPUT_BLACK_ARGS": "",
        "INPUT_OPTIONS": "--check",
        "INPUT_SRC": ".",
        "INPUT_JUPYTER": "false",
        "OUTPUT_FILE": "",
    }.items():
        monkeypatch.setenv(name, value)
    runner = MagicMock(return_value=subprocess.CompletedProcess([], 0, stdout=""))
    monkeypatch.setattr(subprocess, "run", runner)
    return runner


@pytest.mark.parametrize(
    ("config", "specifier"),
    [
        pytest.param(
            '[dependency-groups]\ndev = [{include-group = "base"}, "black==26.5.1"]\n'
            'base = ["pytest"]\n',
            "==26.5.1",
            id="include-before-pin",
        ),
        pytest.param(
            '[dependency-groups]\ndev = ["black==26.5.1", {include-group = "base"}]\n'
            'base = ["pytest"]\n',
            "==26.5.1",
            id="include-after-pin",
        ),
        pytest.param(
            '[dependency-groups]\ndev = [{include-group = "lint"}]\n'
            'lint = ["black==26.5.1"]\n',
            "==26.5.1",
            id="pin-in-included-group",
        ),
        pytest.param(
            '[dependency-groups]\ndev = [{include-group = "base"}]\n'
            'base = ["pytest"]\n[project]\ndependencies = ["black==26.5.1"]\n',
            "==26.5.1",
            id="unrelated-include-before-project-pin",
        ),
        pytest.param(
            '[project]\ndependencies = ["black==26.5.1"]\n',
            "==26.5.1",
            id="project-pin",
        ),
        pytest.param(
            '[dependency-groups]\nlint = ["black[jupyter]>=26; python_version >= '
            "'3.11'\"]\n",
            ">=26",
            id="extras-and-marker",
        ),
    ],
)
def test_action_use_pyproject(
    tmp_path: Path, action_run: MagicMock, config: str, specifier: str
) -> None:
    (tmp_path / "pyproject.toml").write_text(config, encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(ACTION_MAIN), run_name="__main__")

    assert exc.value.code == 0
    assert action_run.call_count == 3
    assert action_run.call_args_list[1].args[0][-1] == f"black[colorama]{specifier}"
    assert action_run.call_args_list[2].args[0][1:] == ["--check", "."]


@pytest.mark.parametrize(
    ("config", "message"),
    [
        pytest.param(
            '[dependency-groups]\nlint = ["black"]\n',
            "Version specifier missing for 'black' dependency",
            id="unpinned-black",
        ),
        pytest.param(
            '[dependency-groups]\ndev = [{include-group = "base"}]\n'
            'base = ["pytest"]\n',
            "'black' dependency missing from pyproject.toml",
            id="include-without-black",
        ),
    ],
)
def test_action_use_pyproject_missing_pin(
    tmp_path: Path,
    action_run: MagicMock,
    capsys: pytest.CaptureFixture[str],
    config: str,
    message: str,
) -> None:
    (tmp_path / "pyproject.toml").write_text(config, encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(ACTION_MAIN), run_name="__main__")

    assert exc.value.code == 1
    assert message in capsys.readouterr().err
    assert action_run.call_count == 1
