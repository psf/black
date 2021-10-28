"""
Check that the rev value in the example from ``the_basics.md`` matches
the latest version of Black. This saves us from forgetting to update that
during the release process.
"""

import os
import sys

import commonmark
from bs4 import BeautifulSoup


def main(changes: str, the_basics: str) -> None:
    changes_html = commonmark.commonmark(changes)
    changes_soup = BeautifulSoup(changes_html, "html.parser")
    headers = changes_soup.find_all("h2")
    tags = [header.string for header in headers if header.string != "Unreleased"]
    latest_tag = tags[0]

    the_basics_html = commonmark.commonmark(the_basics)
    the_basics_soup = BeautifulSoup(the_basics_html, "html.parser")
    (version_example,) = [
        code_block.string
        for code_block in the_basics_soup.find_all(class_="language-console")
        if "$ black --version" in code_block.string
    ]

    for tag in tags:
        if tag in version_example and tag != latest_tag:
            print(
                "Please set the version in the ``black --version`` "
                "example from ``the_basics.md`` to be the latest one.\n"
                f"Expected {latest_tag}, got {tag}.\n"
            )
            sys.exit(1)


if __name__ == "__main__":
    with open("CHANGES.md", encoding="utf-8") as fd:
        changes = fd.read()
    with open(
        os.path.join("docs", "usage_and_configuration", "the_basics.md"),
        encoding="utf-8",
    ) as fd:
        the_basics = fd.read()
    main(changes, the_basics)
