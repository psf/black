"""Helper script for psf/black's diff-shades Github Actions integration.

diff-shades is a tool for analyzing what happens when you run Black on
OSS code capturing it for comparisons or other usage. It's used here to
help measure the impact of a change *before* landing it (in particular
posting a comment on completion for PRs).

This script exists as a more maintainable alternative to using inline
Javascript in the workflow YAML files. The revision configuration and
resolving, caching, and PR comment logic is contained here.

For more information, please see the developer docs:

https://black.readthedocs.io/en/latest/contributing/gauging_changes.html#diff-shades
"""

import json
import os
import platform
import pprint
import subprocess
import sys
from base64 import b64encode
from os.path import dirname, join
from pathlib import Path
from typing import Any, Final

import click
import urllib3
from packaging.version import Version

COMMENT_FILE: Final = ".pr-comment.md"
DIFF_STEP_NAME: Final = "Generate HTML diff report"
DOCS_URL: Final = (
    "https://black.readthedocs.io/en/latest/contributing/gauging_changes.html#diff-shades"
)
SHA_LENGTH: Final = 10
GH_API_TOKEN: Final = os.getenv("GITHUB_TOKEN")
REPO: Final = os.getenv("GITHUB_REPOSITORY", default="psf/black")
USER_AGENT: Final = f"{REPO} diff-shades workflow via urllib3/{urllib3.__version__}"
http = urllib3.PoolManager()


def set_output(name: str, value: str) -> None:
    if len(value) < 200:
        print(f"[INFO]: setting '{name}' to '{value}'")
    else:
        print(f"[INFO]: setting '{name}' to [{len(value)} chars]")

    if "GITHUB_OUTPUT" in os.environ:
        if "\n" in value:
            # https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#multiline-strings
            delimiter = b64encode(os.urandom(16)).decode()
            value = f"{delimiter}\n{value}\n{delimiter}"
            command = f"{name}<<{value}"
        else:
            command = f"{name}={value}"
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            print(command, file=f)


def http_get(url: str, *, is_json: bool = True, **kwargs: Any) -> Any:
    headers = kwargs.get("headers") or {}
    headers["User-Agent"] = USER_AGENT
    if "github" in url:
        if GH_API_TOKEN:
            headers["Authorization"] = f"token {GH_API_TOKEN}"
        headers["Accept"] = "application/vnd.github.v3+json"
    kwargs["headers"] = headers

    r = http.request("GET", url, **kwargs)
    if is_json:
        data = json.loads(r.data.decode("utf-8"))
    else:
        data = r.data
    print(f"[INFO]: issued GET request for {r.geturl()}")
    if not (200 <= r.status < 300):
        pprint.pprint(dict(r.info()))
        pprint.pprint(data)
        raise RuntimeError(f"unexpected status code: {r.status}")

    return data


def get_latest_revision(ref: str) -> str:
    data = http_get(
        f"https://api.github.com/repos/{REPO}/commits",
        fields={"per_page": "1", "sha": ref},
    )
    assert isinstance(data[0]["sha"], str)
    return data[0]["sha"]


def get_pr_branches(pr: int | None = None) -> tuple[Any, Any, int]:
    if not pr:
        pr_ref = os.getenv("GITHUB_REF")
        assert pr_ref is not None
        pr = int(pr_ref[10:-6])

    data = http_get(f"https://api.github.com/repos/{REPO}/pulls/{pr}")
    assert isinstance(data["base"]["sha"], str)
    assert isinstance(data["head"]["sha"], str)
    return data["base"], data["head"], pr


def get_pypi_version() -> Version:
    data = http_get("https://pypi.org/pypi/black/json")
    versions = [Version(v) for v in data["releases"]]
    sorted_versions = sorted(versions, reverse=True)
    return sorted_versions[0]


@click.group()
def main() -> None:
    pass


@main.command("config", help="Acquire run configuration and metadata.")
def config() -> None:
    import diff_shades  # type: ignore[import-not-found]

    jobs = [{"mode": "preview-new-changes", "style": "preview"}]

    event = os.getenv("GITHUB_EVENT_NAME")
    if event == "push":
        # Push on main, let's use PyPI Black as the baseline.
        baseline_name = str(get_pypi_version())
        baseline_cmd = f"git checkout {baseline_name}"

        target_rev = os.getenv("GITHUB_SHA")
        assert target_rev is not None
        target_name = "main-" + target_rev[:SHA_LENGTH]
        target_cmd = f"git checkout {target_rev}"

    elif event == "pull_request":
        jobs.insert(0, {"mode": "assert-no-changes", "style": "stable"})
        # PR, let's use the PR base as the baseline.
        base, head, pr_num = get_pr_branches()

        baseline_rev = get_latest_revision(base["ref"])
        baseline_name = f"{base['ref']}-{baseline_rev[:SHA_LENGTH]}"
        baseline_cmd = f"git checkout {baseline_rev}"

        target_name = f"pr-{pr_num}-{head['sha'][:SHA_LENGTH]}"
        target_cmd = f"gh pr checkout {pr_num}\ngit merge origin/{base['ref']}"
    else:
        raise ValueError(f"Unknown event {event}")

    env = f"{platform.system()}-{platform.python_version()}-{diff_shades.__version__}"
    for entry in jobs:
        entry["baseline-analysis"] = f"{entry['style']}-{baseline_name}.json"
        entry["baseline-setup-cmd"] = baseline_cmd
        entry["baseline-cache-key"] = f"{env}-{baseline_name}-{entry['style']}"

        entry["target-analysis"] = f"{entry['style']}-{target_name}.json"
        entry["target-setup-cmd"] = target_cmd

    set_output("matrix", json.dumps(jobs, indent=None))
    pprint.pprint(jobs)


@main.command("comment-body", help="Generate the body for a summary PR comment.")
@click.argument("baseline", type=click.Path(exists=True, path_type=Path))
@click.argument("target", type=click.Path(exists=True, path_type=Path))
@click.argument("style")
@click.argument("mode")
def comment_body(baseline: Path, target: Path, style: str, mode: str) -> None:
    cmd = (
        f"{sys.executable} -m diff_shades --no-color "
        f"compare {baseline} {target} --quiet --check"
    ).split(" ")
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, encoding="utf-8")
    if proc.returncode:
        run_id = os.getenv("GITHUB_RUN_ID")
        jobs = http_get(
            f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}/jobs",
        )["jobs"]
        job = next(j for j in jobs if j["name"] == f"compare / {mode}")
        diff_step = next(s for s in job["steps"] if s["name"] == DIFF_STEP_NAME)
        diff_url = f"{job['html_url']}#step:{diff_step['number']}:1"

        body = (
            "<details>"
            f"<summary><b><code>--{style}</code> style</b> "
            f'(<a href="{diff_url}">View full diff</a>):</summary>'
            f"<pre>{proc.stdout.strip()}</pre>"
            "</details>"
        )
    else:
        body = f"<b><code>--{style}</code> style</b>: no changes"

    filename = f".{style}{COMMENT_FILE}"
    print(f"[INFO]: writing comment details to {filename}")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(body)


@main.command("comment-details", help="Get PR comment resources from a workflow run.")
@click.argument("pr")
@click.argument("run-id")
@click.argument("styles", nargs=-1)
def comment_details(pr: int, run_id: str, styles: tuple[str, ...]) -> None:
    base, head, _ = get_pr_branches(pr)

    lines = [
        f"**diff-shades** results comparing this PR ({head['sha']}) to {base['ref']}"
        f" ({base['sha']}):"
    ]
    for style_file in styles:
        with open(
            join(dirname(__file__), "..", style_file),
            "r",
            encoding="utf-8",
        ) as f:
            content = f.read()
            lines.append(content)

    lines.append("---")

    lines.append(
        f"[**What is this?**]({DOCS_URL}) | "
        f"[Workflow run](https://github.com/psf/black/actions/runs/{run_id}) | "
        "[diff-shades documentation](https://github.com/ichard26/diff-shades#readme)"
    )

    body = "\n\n".join(lines)
    set_output("comment-body", body)


if __name__ == "__main__":
    main()
