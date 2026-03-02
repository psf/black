"""
Check that the rev value in the example pre-commit configuration matches
the latest version of Black. This saves us from forgetting to update that
during the release process.

Why can't we just use `rev: stable` and call it a day? Well pre-commit
won't auto update the hook as you may expect (and for good reasons, some
technical and some pragmatic). Encouraging bad practice is also just
not ideal. xref: https://github.com/psf/black/issues/420
"""

import os
import sys

import commonmark
import yaml
from bs4 import BeautifulSoup


def main(changes: str, content: str, filename: str) -> None:
    changes_html = commonmark.commonmark(changes)
    changes_soup = BeautifulSoup(changes_html, "html.parser")
    headers = changes_soup.find_all("h2")
    latest_tag, *_ = (
        header.string for header in headers if header.string != "Unreleased"
    )

    source_version_control_html = commonmark.commonmark(content)
    source_version_control_soup = BeautifulSoup(
        source_version_control_html, "html.parser"
    )
    codeblocks = source_version_control_soup.find_all(class_="language-yaml")

    for codeblock in codeblocks:
        parsed = yaml.safe_load(codeblock.string)  # type: ignore[arg-type]
        if not isinstance(parsed, dict):
            return
        pre_commit_rev = parsed["repos"][0]["rev"]
        if not pre_commit_rev == latest_tag:
            print(
                f"Please set the rev in ``{filename}`` to be the latest one.\n"
                f"Expected {latest_tag}, got {pre_commit_rev}.\n"
            )
            sys.exit(1)


if __name__ == "__main__":
    with open("CHANGES.md", encoding="utf-8") as fd:
        changes = fd.read()
    with open(
        os.path.join("docs", "integrations", "source_version_control.md"),
        encoding="utf-8",
    ) as fd:
        content = fd.read()
        main(changes, content, "source_version_control.md")
    with open(
        os.path.join("docs", "guides", "using_black_with_jupyter_notebooks.md"),
        encoding="utf-8",
    ) as fd:
        content = fd.read()
        main(changes, content, "using_black_with_jupyter_notebooks.md")
