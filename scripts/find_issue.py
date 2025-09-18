import random
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, cast

from pysource_codegen import generate
from pysource_minimize import minimize

import black

base_path = Path(__file__).parent


@dataclass()
class Issue:
    src: str
    mode: black.FileMode


def bug_in_code(issue: Issue) -> bool:
    try:
        dst_contents = black.format_str(issue.src, mode=issue.mode)

        black.assert_equivalent(issue.src, dst_contents)
        black.assert_stable(issue.src, dst_contents, mode=issue.mode)
    except Exception:
        return True
    return False


def current_target_version() -> black.TargetVersion:
    v = sys.version_info
    return cast(black.TargetVersion, getattr(black.TargetVersion, f"PY{v[0]}{v[1]}"))


def find_issue() -> Optional[Issue]:
    t = time.time()
    print("search for new issue ", end="", flush=True)

    while time.time() - t < 60 * 10:
        for line_length in (100, 1):
            for magic_trailing_comma in (True, False):
                print(".", end="", flush=True)
                mode = black.FileMode(
                    line_length=line_length,
                    string_normalization=True,
                    is_pyi=False,
                    magic_trailing_comma=magic_trailing_comma,
                    target_versions={current_target_version()},
                )
                seed = random.randint(0, 100000000)

                src_code = generate(seed)

                issue = Issue(src_code, mode)

                if bug_in_code(issue):
                    print(f"\nfound bug (seed={seed})")
                    return issue
    print("\nno new issue found in 10 minutes")
    return None


def minimize_code(issue: Issue) -> Issue:
    minimized = Issue(
        minimize(issue.src, lambda code: bug_in_code(Issue(code, issue.mode))),
        issue.mode,
    )
    assert bug_in_code(minimized)

    print("minimized code:")
    print(minimized.src)

    return minimized


def mode_to_options(mode: black.FileMode) -> list[str]:
    result = ["-l", str(mode.line_length)]
    if not mode.magic_trailing_comma:
        result.append("-C")
    (v,) = list(mode.target_versions)
    result += ["-t", v.name.lower()]
    return result


def create_link(issue: Issue) -> str:
    import base64
    import json
    import lzma

    data = {
        "sc": issue.src,
        "ll": issue.mode.line_length,
        "ssfl": issue.mode.skip_source_first_line,
        "ssn": not issue.mode.string_normalization,
        "smtc": not issue.mode.magic_trailing_comma,
        "pyi": issue.mode.is_pyi,
        "fast": False,
        "prv": issue.mode.preview,
        "usb": issue.mode.unstable,
        "tv": [v.name.lower() for v in issue.mode.target_versions],
    }

    compressed = lzma.compress(json.dumps(data).encode("utf-8"))
    state = base64.urlsafe_b64encode(compressed).decode("utf-8")

    return f"https://black.vercel.app/?version=main&state={state}"


def create_issue(issue: Issue) -> str:

    dir = tempfile.TemporaryDirectory()

    cwd = Path(dir.name)
    bug_file = cwd / "bug.py"
    bug_file.write_text(issue.src)

    multiline_code = "\n".join(["    " + repr(s + "\n") for s in issue.src.split("\n")])

    parse_code = f"""\
from ast import parse
parse(
{multiline_code}
)
"""
    cwd = Path(dir.name)
    (cwd / "parse_code.py").write_text(parse_code)
    command = ["black", *mode_to_options(issue.mode), "bug.py"]

    format_result = subprocess.run(
        [sys.executable, "-m", *command], capture_output=True, cwd=cwd
    )

    fast_command = [*command, "--fast"]
    format_fast_result = subprocess.run(
        [sys.executable, "-m", *fast_command], capture_output=True, cwd=cwd
    )

    fast_formatted = ""
    if format_fast_result.returncode == 0:
        fast_formatted = f"""
The code can be formatted with `{" ".join(fast_command)}`:
``` python
{bug_file.read_text().rstrip()}
```"""

    error_output = format_result.stderr.decode()

    m = re.search("This diff might be helpful: (/.*)", error_output)
    reported_diff = ""
    if m:
        path = Path(m[1])
        reported_diff = f"""
the reported diff in {path} is:
``` diff
{path.read_text().rstrip()}
```"""

    run_result = subprocess.run(
        [sys.executable, "parse_code.py"], capture_output=True, cwd=cwd
    )

    assert (
        run_result.returncode == 0
    ), "pysource-codegen should only generate code which can be parsed"

    git_ref = subprocess.run(
        ["git", "rev-parse", "origin/main"], capture_output=True
    ).stdout

    return f"""
**Describe the bug**

The following code can not be parsed/formatted by black:

``` python
{issue.src}
```
([playground]({create_link(issue)}))

black reported the following error:
```
> {" ".join(command)}
{format_result.stderr.decode().rstrip()}
```
{reported_diff}

but it can be parsed by cpython:
``` python
{parse_code.rstrip()}
```
{fast_formatted}

**Environment**

<!-- Please complete the following information: -->

- Black's version: current main ({git_ref.decode().strip()})
- OS and Python version: Linux/Python {sys.version}

**Additional context**

The bug was found by pysource-codegen (see #3908)
The above problem description was created from a script,
let me know if you think it can be improved.
"""


def main() -> None:
    issue = find_issue()
    if issue is None:
        return

    issue = minimize_code(issue)

    while issue.mode.line_length > 1 and bug_in_code(issue):
        issue.mode.line_length -= 1
    issue.mode.line_length += 1

    issue = minimize_code(issue)

    while issue.mode.line_length <= 100 and bug_in_code(issue):
        issue.mode.line_length += 1
    issue.mode.line_length -= 1

    issue = minimize_code(issue)

    print(create_issue(issue))


if __name__ == "__main__":
    main()
