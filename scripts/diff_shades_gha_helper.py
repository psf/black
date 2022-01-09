import json
import os
import platform
import pprint
import subprocess
import sys
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import click
import urllib3
from packaging.version import Version

if sys.version_info >= (3, 8):
    from typing import Final, Literal
else:
    from typing_extensions import Final, Literal

COMMENT_BODY_FILE: Final = ".pr-comment-body.md"
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


def http_get(
    url: str,
    is_json: bool = True,
    headers: Optional[Dict[str, str]] = None,
    **kwargs: Any,
) -> Any:
    headers = headers or {}
    headers["User-Agent"] = USER_AGENT
    if "github" in url:
        if GH_API_TOKEN:
            headers["Authorization"] = f"token {GH_API_TOKEN}"
        headers["Accept"] = "application/vnd.github.v3+json"
    r = http.request("GET", url, headers=headers, **kwargs)
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


def get_branch_or_tag_revision(sha: str = "main") -> str:
    data = http_get(
        f"https://api.github.com/repos/{REPO}/commits",
        fields={"per_page": "1", "sha": sha},
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


def resolve_custom_ref(ref: str) -> Tuple[str, str]:
    if ref == ".pypi":
        # Special value to get latest PyPI version.
        version = str(get_pypi_version())
        return version, f"git checkout {version}"

    if ref.startswith(".") and ref[1:].isnumeric():
        # Special format to get a PR.
        number = int(ref[1:])
        revision = get_pr_revision(number)
        return f"pr-{number}-{revision[:SHA_LENGTH]}", f"gh pr checkout {number}"

    # Alright, it's probably a branch, tag, or a commit SHA, let's find out!
    revision = get_branch_or_tag_revision(ref)
    # We're cutting the revision short as we might be operating on a short commit SHA.
    if revision == ref or revision[: len(ref)] == ref:
        # It's *probably* a commit as the resolved SHA isn't different from the REF.
        return revision[:SHA_LENGTH], f"git checkout {revision}"

    # It's *probably* a pre-existing branch or tag, yay!
    return f"{ref}-{revision[:SHA_LENGTH]}", f"git checkout {revision}"


@click.group()
def main() -> None:
    pass


@main.command("config", help="Acquire run configuration and metadata.")
@click.argument(
    "event", type=click.Choice(["push", "pull_request", "workflow_dispatch"])
)
@click.argument("custom_baseline", required=False)
@click.argument("custom_target", required=False)
@click.option("--baseline-args", default="")
def config(
    event: Literal["push", "pull_request", "workflow_dispatch"],
    custom_baseline: Optional[str],
    custom_target: Optional[str],
    baseline_args: str,
) -> None:
    import diff_shades

    if event == "push":
        # Push on main, let's use PyPI Black as the baseline.
        baseline_name = str(get_pypi_version())
        baseline_cmd = f"git checkout {baseline_name}"
        target_rev = os.getenv("GITHUB_SHA")
        assert target_rev is not None
        target_name = "main-" + target_rev[:SHA_LENGTH]
        target_cmd = f"git checkout {target_rev}"

    elif event == "pull_request":
        # PR, let's use main as the baseline.
        baseline_rev = get_branch_or_tag_revision()
        assert baseline_rev is not None, "main should exist ..."
        baseline_name = "main-" + baseline_rev[:SHA_LENGTH]
        baseline_cmd = f"git checkout {baseline_rev}"

        pr_ref = os.getenv("GITHUB_REF")
        assert pr_ref is not None
        pr_num = int(pr_ref[10:-6])
        pr_rev = get_pr_revision(pr_num)
        target_name = f"pr-{pr_num}-{pr_rev[:SHA_LENGTH]}"
        target_cmd = f"gh pr checkout {pr_num} && git merge origin/main"

        # These are only needed for the PR comment.
        set_output("baseline-sha", baseline_rev)
        set_output("target-sha", pr_rev)
    else:
        assert custom_baseline is not None and custom_target is not None
        baseline_name, baseline_cmd = resolve_custom_ref(custom_baseline)
        target_name, target_cmd = resolve_custom_ref(custom_target)
        if baseline_name == target_name:
            # Alright we're using the same revisions but we're (hopefully) using
            # different command line arguments, let's support that too.
            baseline_name += "-1"
            target_name += "-2"

    set_output("baseline-analysis", baseline_name + ".json")
    set_output("baseline-setup-cmd", baseline_cmd)
    set_output("target-analysis", target_name + ".json")
    set_output("target-setup-cmd", target_cmd)

    key = f"{platform.system()}-{platform.python_version()}-{diff_shades.__version__}"
    key += f"-{baseline_name}-{baseline_args.encode('utf-8').hex()}"
    set_output("baseline-cache-key", key)


@main.command("comment-body", help="Generate the body for a summary PR comment.")
@click.argument("baseline", type=click.Path(exists=True, path_type=Path))
@click.argument("target", type=click.Path(exists=True, path_type=Path))
@click.argument("baseline-sha")
@click.argument("target-sha")
def comment_body(
    baseline: Path, target: Path, baseline_sha: str, target_sha: str
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
            '($job-diff-url) under the "Generate HTML diff report" step.'
        )
        body += "\n```text\n" + proc.stdout.strip() + "\n```\n"
    body += (
        f"[**What is this?**]({DOCS_URL}) | [Workflow run]($workflow-run-url) |"
        " [diff-shades documentation](https://github.com/ichard26/diff-shades#readme) |"
        # This is used by the comment workflow to discover a pre-existing comment.
        " id: diff-shades-comment"
    )
    print(f"[INFO]: writing half-completed comment body to {COMMENT_BODY_FILE}")
    with open(COMMENT_BODY_FILE, "w", encoding="utf-8") as f:
        f.write(body)


@main.command("comment-details", help="Get PR comment resources from a workflow run.")
@click.argument("run-id")
def comment_details(run_id: str) -> None:
    data = http_get(f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}")
    if data["event"] != "pull_request":
        set_output("needs-comment", "false")
        return

    set_output("needs-comment", "true")
    pulls = data["pull_requests"]
    assert len(pulls) == 1
    pr_number = pulls[0]["number"]
    set_output("pr-number", str(pr_number))

    jobs_data = http_get(data["jobs_url"])
    job = jobs_data["jobs"][0]
    steps = {s["name"]: s["number"] for s in job["steps"]}
    diff_step = steps["Generate HTML diff report"]
    diff_url = job["html_url"] + f"#step:{diff_step}:1"

    artifacts_data = http_get(data["artifacts_url"])["artifacts"]
    artifacts = {a["name"]: a["archive_download_url"] for a in artifacts_data}
    body_url = artifacts[COMMENT_BODY_FILE]
    body_zip = BytesIO(http_get(body_url, is_json=False))
    with zipfile.ZipFile(body_zip) as zfile:
        with zfile.open(COMMENT_BODY_FILE) as rf:
            body = rf.read().decode("utf-8")
    # It's more convenient to fill these fields after the first workflow is done
    # since this command can access the workflows API.
    body = body.replace("$workflow-run-url", data["html_url"])
    body = body.replace("$job-diff-url", diff_url)
    # # https://github.community/t/set-output-truncates-multiline-strings/16852/3
    escaped = body.replace("%", "%25").replace("\n", "%0A").replace("\r", "%0D")
    set_output("comment-body", escaped)


if __name__ == "__main__":
    main()
