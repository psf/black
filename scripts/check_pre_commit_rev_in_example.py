import os

import commonmark
import yaml
from bs4 import BeautifulSoup


def main(changes: str, source_version_control: str) -> None:
    html = commonmark.commonmark(changes)
    soup = BeautifulSoup(html, "html.parser")
    latest_version = [
        header.string for header in soup.find_all("h2") if header.string != "Unreleased"
    ][0]

    html = commonmark.commonmark(source_version_control)
    soup = BeautifulSoup(html, "html.parser")
    pre_commit_repos = yaml.safe_load(soup.find(class_="language-yaml").string)["repos"]
    if not all(repo["rev"] == latest_version for repo in pre_commit_repos):
        raise ValueError(
            "Please set the rev in ``source_version_control.md`` to be the latest one\n"
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
