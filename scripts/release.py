#!/usr/bin/env python3

from __future__ import annotations

"""
Tool to help automate changes needed in commits during and after releases
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from subprocess import PIPE, run
from typing import List

LOG = logging.getLogger(__name__)
NEW_VERSION_CHANGELOG_TEMPLATE = """\
## Unreleased

### Highlights

<!-- Include any especially major or disruptive changes here -->

### Stable style

<!-- Changes that affect Black's stable style -->

### Preview style

<!-- Changes that affect Black's preview style -->

### Configuration

<!-- Changes to how Black can be configured -->

### Packaging

<!-- Changes to how Black is packaged, such as dependency requirements -->

### Parser

<!-- Changes to the parser or to version autodetection -->

### Performance

<!-- Changes that improve Black's performance. -->

### Output

<!-- Changes to Black's terminal output and error messages -->

### _Blackd_

<!-- Changes to blackd -->

### Integrations

<!-- For example, Docker, GitHub Actions, pre-commit, editors -->

### Documentation

<!-- Major changes to documentation and policies. Small docs changes
     don't need a changelog entry. -->
"""


class NoGitTagsError(Exception): ...  # noqa: E701,E761


# TODO: Do better with alpha + beta releases
# Maybe we vendor packaging library
def get_git_tags(versions_only: bool = True) -> List[str]:
    """Pull out all tags or calvers only"""
    cp = run(["git", "tag"], stdout=PIPE, stderr=PIPE, check=True, encoding="utf8")
    if not cp.stdout:
        LOG.error(f"Returned no git tags stdout: {cp.stderr}")
        raise NoGitTagsError
    git_tags = cp.stdout.splitlines()
    if versions_only:
        return [t for t in git_tags if t[0].isdigit()]
    return git_tags


# TODO: Support sorting alhpa/beta releases correctly
def tuple_calver(calver: str) -> tuple[int, ...]:  # mypy can't notice maxsplit below
    """Convert a calver string into a tuple of ints for sorting"""
    try:
        return tuple(map(int, calver.split(".", maxsplit=2)))
    except ValueError:
        return (0, 0, 0)


class SourceFiles:
    def __init__(self, black_repo_dir: Path):
        # File path fun all pathlib to be platform agnostic
        self.black_repo_path = black_repo_dir
        self.changes_path = self.black_repo_path / "CHANGES.md"
        self.docs_path = self.black_repo_path / "docs"
        self.version_doc_paths = (
            self.docs_path / "integrations" / "source_version_control.md",
            self.docs_path / "usage_and_configuration" / "the_basics.md",
        )
        self.current_version = self.get_current_version()
        self.next_version = self.get_next_version()

    def __str__(self) -> str:
        return f"""\
> SourceFiles ENV:
  Repo path: {self.black_repo_path}
  CHANGES.md path: {self.changes_path}
  docs path: {self.docs_path}
  Current version: {self.current_version}
  Next version: {self.next_version}
"""

    def add_template_to_changes(self) -> int:
        """Add the template to CHANGES.md if it does not exist"""
        LOG.info(f"Adding template to {self.changes_path}")

        with self.changes_path.open("r") as cfp:
            changes_string = cfp.read()

        if "## Unreleased" in changes_string:
            LOG.error(f"{self.changes_path} already has unreleased template")
            return 1

        templated_changes_string = changes_string.replace(
            "# Change Log\n",
            f"# Change Log\n\n{NEW_VERSION_CHANGELOG_TEMPLATE}",
        )

        with self.changes_path.open("w") as cfp:
            cfp.write(templated_changes_string)

        LOG.info(f"Added template to {self.changes_path}")
        return 0

    def cleanup_changes_template_for_release(self) -> None:
        LOG.info(f"Cleaning up {self.changes_path}")

        with self.changes_path.open("r") as cfp:
            changes_string = cfp.read()

        # Change Unreleased to next version
        versioned_changes = changes_string.replace(
            "## Unreleased", f"## {self.next_version}"
        )

        # Remove all comments (subheadings are harder - Human required still)
        no_comments_changes = []
        for line in versioned_changes.splitlines():
            if line.startswith("<!--") or line.endswith("-->"):
                continue
            no_comments_changes.append(line)

        with self.changes_path.open("w") as cfp:
            cfp.write("\n".join(no_comments_changes) + "\n")

        LOG.debug(f"Finished Cleaning up {self.changes_path}")

    def get_current_version(self) -> str:
        """Get the latest git (version) tag as latest version"""
        return sorted(get_git_tags(), key=lambda k: tuple_calver(k))[-1]

    def get_next_version(self) -> str:
        """Workout the year and month + version number we need to move to"""
        base_calver = datetime.today().strftime("%y.%m")
        calver_parts = base_calver.split(".")
        base_calver = f"{calver_parts[0]}.{int(calver_parts[1])}"  # Remove leading 0
        git_tags = get_git_tags()
        same_month_releases = [
            t for t in git_tags if t.startswith(base_calver) and "a" not in t
        ]
        if len(same_month_releases) < 1:
            return f"{base_calver}.0"
        same_month_version = same_month_releases[-1].split(".", 2)[-1]
        return f"{base_calver}.{int(same_month_version) + 1}"

    def update_repo_for_release(self) -> int:
        """Update CHANGES.md + doc files ready for release"""
        self.cleanup_changes_template_for_release()
        self.update_version_in_docs()
        return 0  # return 0 if no exceptions hit

    def update_version_in_docs(self) -> None:
        for doc_path in self.version_doc_paths:
            LOG.info(f"Updating black version to {self.next_version} in {doc_path}")

            with doc_path.open("r") as dfp:
                doc_string = dfp.read()

            next_version_doc = doc_string.replace(
                self.current_version, self.next_version
            )

            with doc_path.open("w") as dfp:
                dfp.write(next_version_doc)

            LOG.debug(
                f"Finished updating black version to {self.next_version} in {doc_path}"
            )


def _handle_debug(debug: bool) -> None:
    """Turn on debugging if asked otherwise INFO default"""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s: %(message)s (%(filename)s:%(lineno)d)",
        level=log_level,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--add-changes-template",
        action="store_true",
        help="Add the Unreleased template to CHANGES.md",
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Verbose debug output"
    )
    args = parser.parse_args()
    _handle_debug(args.debug)
    return args


def main() -> int:
    args = parse_args()

    # Need parent.parent cause script is in scripts/ directory
    sf = SourceFiles(Path(__file__).parent.parent)

    if args.add_changes_template:
        return sf.add_template_to_changes()

    LOG.info(f"Current version detected to be {sf.current_version}")
    LOG.info(f"Next version will be {sf.next_version}")
    return sf.update_repo_for_release()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
