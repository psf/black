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
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any

import click
import urllib3
from packaging.version import Version

if sys.version_info >= (3, 8):
    from typing import Final, Literal
else:
    from typing_extensions import Final, Literal

COMMENT_FILE: Final = ".pr-comment.json"
DIFF_STEP_NAME: Final = "Generate HTML diff report"
DOCS_URL: Final = (
    "https://black.readthedocs.io/en/latest/"
    "contributing/gauging_changes.html#diff-shades"
)
USER_AGENT: Final = f"psf/black diff-shades workflow via urllib3/{urllib3.__version__}"
SHA_LENGTH: Final = 10
GH_API_TOKEN: Final = os.getenv("GITHUB_TOKEN")
REPO: Final = os.getenv("GITHUB_REPOSITORY", default="psf/black")
http = urllib3.PoolManager()


def set_output(name: str, value: str) -> None:
    if len(value) < 200:
        print(f"[INFO]: setting '{name}' to '{value}'")
    else:
        print(f"[INFO]: setting '{name}' to [{len(value)} chars]")
    print(f"::set-output name={name}::{value}")


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


def get_main_revision() -> str:
    data = http_get(
        f"https://api.github.com/repos/{REPO}/commits",
        fields={"per_page": "1", "sha": "main"},
    )
    assert isinstance(data[0]["sha"], str)
    return data[0]["sha"]


def get_pr_revision(pr: int) -> str:
    data = http_get(f"https://api.github.com/repos/{REPO}/pulls/{pr}")
    assert isinstance(data["head"]["sha"], str)
    return data["head"]["sha"]


def get_pypi_version() -> Version:
    data = http_get("https://pypi.org/pypi/black/json")
    versions = [Version(v) for v in data["releases"]]
    sorted_versions = sorted(versions, reverse=True)
    return sorted_versions[0]


@click.group()
def main() -> None:
    pass


@main.command("config", help="Acquire run configuration and metadata.")
@click.argument("event", type=click.Choice(["push", "pull_request"]))
def config(event: Literal["push", "pull_request"]) -> None:
    import diff_shades

    if event == "push":
        jobs = [{"mode": "preview-changes", "force-flag": "--force-preview-style"}]
        # Push on main, let's use PyPI Black as the baseline.
        baseline_name = str(get_pypi_version())
        baseline_cmd = f"git checkout {baseline_name}"
        target_rev = os.getenv("GITHUB_SHA")
        assert target_rev is not None
        target_name = "main-" + target_rev[:SHA_LENGTH]
        target_cmd = f"git checkout {target_rev}"

    elif event == "pull_request":
        jobs = [
            {"mode": "preview-changes", "force-flag": "--force-preview-style"},
            {"mode": "assert-no-changes", "force-flag": "--force-stable-style"},
        ]
        # PR, let's use main as the baseline.
        baseline_rev = get_main_revision()
        baseline_name = "main-" + baseline_rev[:SHA_LENGTH]
        baseline_cmd = f"git checkout {baseline_rev}"
        pr_ref = os.getenv("GITHUB_REF")
        assert pr_ref is not None
        pr_num = int(pr_ref[10:-6])
        pr_rev = get_pr_revision(pr_num)
        target_name = f"pr-{pr_num}-{pr_rev[:SHA_LENGTH]}"
        target_cmd = f"gh pr checkout {pr_num} && git merge origin/main"

    env = f"{platform.system()}-{platform.python_version()}-{diff_shades.__version__}"
    for entry in jobs:
        entry["baseline-analysis"] = f"{entry['mode']}-{baseline_name}.json"
        entry["baseline-setup-cmd"] = baseline_cmd
        entry["target-analysis"] = f"{entry['mode']}-{target_name}.json"
        entry["target-setup-cmd"] = target_cmd
        entry["baseline-cache-key"] = f"{env}-{baseline_name}-{entry['mode']}"
        if event == "pull_request":
            # These are only needed for the PR comment.
            entry["baseline-sha"] = baseline_rev
            entry["target-sha"] = pr_rev

    set_output("matrix", json.dumps(jobs, indent=None))
    pprint.pprint(jobs)


@main.command("comment-body", help="Generate the body for a summary PR comment.")
@click.argument("baseline", type=click.Path(exists=True, path_type=Path))
@click.argument("target", type=click.Path(exists=True, path_type=Path))
@click.argument("baseline-sha")
@click.argument("target-sha")
@click.argument("pr-num", type=int)
def comment_body(
    baseline: Path, target: Path, baseline_sha: str, target_sha: str, pr_num: int
) -> None:
    # fmt: off
    cmd = [
        sys.executable, "-m", "diff_shades", "--no-color",
        "compare", str(baseline), str(target), "--quiet", "--check"
    ]
    # fmt: on
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, encoding="utf-8")
    if not proc.returncode:
        body = (
            f"**diff-shades** reports zero changes comparing this PR ({target_sha}) to"
            f" main ({baseline_sha}).\n\n---\n\n"
        )
    else:
        body = (
            f"**diff-shades** results comparing this PR ({target_sha}) to main"
            f" ({baseline_sha}). The full diff is [available in the logs]"
            f'($job-diff-url) under the "{DIFF_STEP_NAME}" step.'
        )
        body += "\n```text\n" + proc.stdout.strip() + "\n```\n"
    body += (
        f"[**What is this?**]({DOCS_URL}) | [Workflow run]($workflow-run-url) |"
        " [diff-shades documentation](https://github.com/ichard26/diff-shades#readme)"
    )
    print(f"[INFO]: writing comment details to {COMMENT_FILE}")
    with open(COMMENT_FILE, "w", encoding="utf-8") as f:
        json.dump({"body": body, "pr-number": pr_num}, f)


@main.command("comment-details", help="Get PR comment resources from a workflow run.")
@click.argument("run-id")
def comment_details(run_id: str) -> None:
    data = http_get(f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}")
    if data["event"] != "pull_request" or data["conclusion"] == "cancelled":
        set_output("needs-comment", "false")
        return

    set_output("needs-comment", "true")
    jobs = http_get(data["jobs_url"])["jobs"]
    job = next(j for j in jobs if j["name"] == "analysis / preview-changes")
    diff_step = next(s for s in job["steps"] if s["name"] == DIFF_STEP_NAME)
    diff_url = job["html_url"] + f"#step:{diff_step['number']}:1"

    artifacts = http_get(data["artifacts_url"])["artifacts"]
    comment_artifact = next(a for a in artifacts if a["name"] == COMMENT_FILE)
    comment_url = comment_artifact["archive_download_url"]
    comment_zip = BytesIO(http_get(comment_url, is_json=False))
    with zipfile.ZipFile(comment_zip) as zfile:
        with zfile.open(COMMENT_FILE) as rf:
            comment_data = json.loads(rf.read().decode("utf-8"))

    set_output("pr-number", str(comment_data["pr-number"]))
    body = comment_data["body"]
    # It's more convenient to fill in these fields after the first workflow is done
    # since this command can access the workflows API (doing it in the main workflow
    # while it's still in progress seems impossible).
    body = body.replace("$workflow-run-url", data["html_url"])
    body = body.replace("$job-diff-url", diff_url)
    # https://github.community/t/set-output-truncates-multiline-strings/16852/3
    escaped = body.replace("%", "%25").replace("\n", "%0A").replace("\r", "%0D")
    set_output("comment-body", escaped)


if __name__ == "__main__":
    main()
