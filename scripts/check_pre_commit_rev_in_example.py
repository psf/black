import os

import commonmark
import yaml
from bs4 import BeautifulSoup


def main(changes: str, source_version_control: str) -> None:
    changes_html = commonmark.commonmark(changes)
    changes_soup = BeautifulSoup(changes_html, "html.parser")
    headers = changes_soup.find_all("h2")
    latest_tag, *_ = [
        header.string for header in headers if header.string != "Unreleased"
    ]

    source_version_control_html = commonmark.commonmark(source_version_control)
    source_version_control_soup = BeautifulSoup(
        source_version_control_html, "html.parser"
    )
    pre_commit_repos = yaml.safe_load(
        source_version_control_soup.find(class_="language-yaml").string
    )["repos"]

    for repo in pre_commit_repos:
        pre_commit_rev = repo["rev"]
        if not pre_commit_rev == latest_tag:
            raise ValueError(
                "Please set the rev in ``source_version_control.md`` to be the latest "
                f"one.\nExpected {latest_tag}, got {pre_commit_rev}\n"
            )


if __name__ == "__main__":
    with open("CHANGES.md", encoding="utf-8") as fd:
        changes = fd.read()
    with open(
        os.path.join("docs", "integrations", "source_version_control.md"),
        encoding="utf-8",
    ) as fd:
        source_version_control = fd.read()
    main(changes, source_version_control)
