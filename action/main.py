import os
import shlex
import sys
from pathlib import Path
from re import MULTILINE, search
from subprocess import PIPE, STDOUT, run

ACTION_PATH = Path(os.environ["GITHUB_ACTION_PATH"])
GITHUB_OUTPUT = Path(os.environ["GITHUB_OUTPUT"])
ENV_PATH = ACTION_PATH / ".black-env"
ENV_BIN = ENV_PATH / ("Scripts" if sys.platform == "win32" else "bin")
OPTIONS = os.getenv("INPUT_OPTIONS", default="")
SRC = os.getenv("INPUT_SRC", default="")
JUPYTER = os.getenv("INPUT_JUPYTER") == "true"
BLACK_ARGS = os.getenv("INPUT_BLACK_ARGS", default="")
VERSION = os.getenv("INPUT_VERSION", default="")

_is_formatted_re = r"\s?(?P<changed-files>[0-9]+)\sfiles?\sreformatted(\.|,)\s?"

_outputs = {"is-formatted": "false", "changed-files": "0"}

run([sys.executable, "-m", "venv", str(ENV_PATH)], check=True)

version_specifier = VERSION
if VERSION and VERSION[0] in "0123456789":
    version_specifier = f"=={VERSION}"
if JUPYTER:
    extra_deps = "[colorama,jupyter]"
else:
    extra_deps = "[colorama]"
if version_specifier:
    req = f"black{extra_deps}{version_specifier}"
else:
    describe_name = ""
    with open(ACTION_PATH / ".git_archival.txt", encoding="utf-8") as fp:
        for line in fp:
            if line.startswith("describe-name: "):
                describe_name = line[len("describe-name: ") :].rstrip()
                break
    if not describe_name:
        print("::error::Failed to detect action version.", flush=True)
        sys.exit(1)
    # expected format is one of:
    # - 23.1.0
    # - 23.1.0-51-g448bba7
    if describe_name.count("-") < 2:
        # the action's commit matches a tag exactly, install exact version from PyPI
        req = f"black{extra_deps}=={describe_name}"
    else:
        # the action's commit does not match any tag, install from the local git repo
        req = f".{extra_deps}"
print(f"Installing {req}...", flush=True)
pip_proc = run(
    [str(ENV_BIN / "python"), "-m", "pip", "install", req],
    stdout=PIPE,
    stderr=STDOUT,
    encoding="utf-8",
    cwd=ACTION_PATH,
)
if pip_proc.returncode:
    print(pip_proc.stdout)
    print("::error::Failed to install Black.", flush=True)
    sys.exit(pip_proc.returncode)


base_cmd = [str(ENV_BIN / "black")]
if BLACK_ARGS:
    # TODO: remove after a while since this is deprecated in favour of SRC + OPTIONS.
    proc = run([*base_cmd, *shlex.split(BLACK_ARGS)], stderr=PIPE)
else:
    proc = run(
        [*base_cmd, *shlex.split(OPTIONS), *shlex.split(SRC)],
        stderr=PIPE
    )
# Re-emit stderr back to console so that action output is visible to pipeline
# Do note, click will strip terminal control codes if the output is not TTY
# and thus, this will not show colors anymore.
print(proc.stderr, file=sys.stderr, flush=True)

_output = proc.stderr.decode("utf-8")
matches = search(_is_formatted_re, _output, MULTILINE)
if matches:
    _outputs["is-formatted"] = "true"
    _outputs["changed-files"] = str(matches.group("changed-files"))

with GITHUB_OUTPUT.open("a+", encoding="utf-8") as f:
    for k, v in _outputs.items():
        f.write(f"{k}={v}\n")

sys.exit(proc.returncode)
