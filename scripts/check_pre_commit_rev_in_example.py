import os
import shlex
import subprocess

import commonmark
import yaml
from bs4 import BeautifulSoup


def main(source_version_control: str) -> None:
    latest_tag = subprocess.run(
        ["git", "describe", "--abbrev=0", "--tags"],
        universal_newlines=True,
        stdout=subprocess.PIPE,
    ).stdout.rstrip()
    if not latest_tag:
        # Running in CI
        latest_tag = subprocess.run(
            shlex.split(
                "curl -sSL api.github.com/repos/psf/black/releases/latest "
                '| grep \'"tag_name":\' | sed -E \'s/.*"([^"]+)".*/\1/\''
            ),
            universal_newlines=True,
            stdout=subprocess.PIPE,
        ).stdout.rstrip()

    html = commonmark.commonmark(source_version_control)
    soup = BeautifulSoup(html, "html.parser")
    pre_commit_repos = yaml.safe_load(soup.find(class_="language-yaml").string)["repos"]

    for repo in pre_commit_repos:
        pre_commit_rev = repo["rev"]
        if not pre_commit_rev == latest_tag:
            raise ValueError(
                "Please set the rev in ``source_version_control.md`` to be the latest "
                f"one.\nExpected {latest_tag}, got {pre_commit_rev}\n"
            )


if __name__ == "__main__":
    with open(
        os.path.join("docs", "integrations", "source_version_control.md"),
        encoding="utf-8",
    ) as fd:
        source_version_control = fd.read()
    main(source_version_control)
