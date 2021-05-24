import os
import shlex
import sys
from pathlib import Path
from subprocess import run, PIPE, STDOUT

ACTION_PATH = Path(os.environ["GITHUB_ACTION_PATH"])
ENV_PATH = ACTION_PATH / ".black-env"
ENV_BIN = ENV_PATH / ("Scripts" if sys.platform == "win32" else "bin")
OPTIONS = os.getenv("INPUT_OPTIONS", default="")
SRC = os.getenv("INPUT_SRC", default="")
BLACK_ARGS = os.getenv("INPUT_BLACK_ARGS", default="")
VERSION = os.getenv("INPUT_VERSION", default="")

# TODO: Uncomment these once https://github.com/actions/runner/issues/664 is resolved,
# right now these cause more confusion than clarity :(
# print("::group:: Setup & Install Black")

run([sys.executable, "-m", "venv", str(ENV_PATH)], check=True)
# print(f"Created virtual environment at `{ENV_PATH!s}`.")

req = "black[colorama,python2]"
if VERSION:
    req += f"=={VERSION}"
# TODO: remove output capturing / hiding once the log grouping works (because the logs
# aren't out of order)
pip_proc = run(
    [str(ENV_BIN / "python"), "-m", "pip", "install", req],
    stdout=PIPE,
    stderr=STDOUT,
    encoding="utf-8",
)
if pip_proc.returncode:
    print(pip_proc.stdout)
    print("::error::Failed to install Black.")
    sys.exit(pip_proc.returncode)

# print("::endgroup::")
# print("::group:: Run Black")

base_cmd = [str(ENV_BIN / "black")]
if BLACK_ARGS:
    # TODO: remove after a while since this is deprecated in favour of SRC + OPTIONS.
    print(
        "::warning::Input `with.black_args` is deprecated. Use `with.options` and `with.src` instead."
    )
    proc = run([*base_cmd, *shlex.split(BLACK_ARGS)])
else:
    proc = run([*base_cmd, *shlex.split(OPTIONS), *shlex.split(SRC)])

# print("::endgroup::")
sys.exit(proc.returncode)
