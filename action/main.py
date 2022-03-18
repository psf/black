import os
import shlex
import sys
from pathlib import Path
from subprocess import PIPE, STDOUT, run

ACTION_PATH = Path(os.environ["GITHUB_ACTION_PATH"])
ENV_PATH = ACTION_PATH / ".black-env"
ENV_BIN = ENV_PATH / ("Scripts" if sys.platform == "win32" else "bin")
OPTIONS = os.getenv("INPUT_OPTIONS", default="")
SRC = os.getenv("INPUT_SRC", default="")
BLACK_ARGS = os.getenv("INPUT_BLACK_ARGS", default="")
VERSION = os.getenv("INPUT_VERSION", default="")

run([sys.executable, "-m", "venv", str(ENV_PATH)], check=True)

req = "black[colorama]"
if VERSION:
    req += f"=={VERSION}"
pip_proc = run(
    [str(ENV_BIN / "python"), "-m", "pip", "install", req],
    stdout=PIPE,
    stderr=STDOUT,
    encoding="utf-8",
)
if pip_proc.returncode:
    print(pip_proc.stdout)
    print("::error::Failed to install Black.", flush=True)
    sys.exit(pip_proc.returncode)


base_cmd = [str(ENV_BIN / "black")]
if BLACK_ARGS:
    # TODO: remove after a while since this is deprecated in favour of SRC + OPTIONS.
    proc = run([*base_cmd, *shlex.split(BLACK_ARGS)])
else:
    proc = run([*base_cmd, *shlex.split(OPTIONS), *shlex.split(SRC)])

sys.exit(proc.returncode)
