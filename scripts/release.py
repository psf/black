#!/usr/bin/env python3

"""
Tool to help automate changes needed in commits during and after releases
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from subprocess import run

from packaging.version import InvalidVersion, Version

LOG = logging.getLogger(__name__)
NEW_VERSION_CHANGELOG_TEMPLATE = """\
## Unreleased

<!-- PR authors:
     Please include the PR number in the changelog entry, not the issue number -->

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

<!-- Changes to Blackd -->

### Integrations

<!-- For example, Docker, GitHub Actions, pre-commit, editors -->

### Documentation

<!-- Major changes to documentation and policies.
     Small docs changes don't need a changelog entry. -->
"""


class NoGitTagsError(Exception): ...


def is_valid_version(version: str, include_pre: bool) -> bool:
    try:
        parsed = Version(version)
        return include_pre or parsed.base_version == str(parsed)
    except InvalidVersion:
        return False


def get_git_tags(include_pre: bool = False) -> list[str]:
    """List all git version tags"""
    cp = run(["git", "tag"], capture_output=True, check=True, encoding="utf8")
    if not cp.stdout:
        LOG.error(f"Returned no git tags; stderr: {cp.stderr}")
        raise NoGitTagsError
    git_tags = cp.stdout.splitlines()
    return sorted(
        (t for t in git_tags if is_valid_version(t, include_pre)),
        key=Version,
        reverse=True,
    )


class SourceFiles:
    def __init__(self, black_repo_dir: Path, version_override: str | None):
        # Use pathlib for all file path fun to be platform agnostic
        self.black_repo_path = black_repo_dir
        self.changes_path = self.black_repo_path / "CHANGES.md"
        self.docs_path = self.black_repo_path / "docs"
        self.version_doc_paths = (
            self.docs_path / "integrations" / "source_version_control.md",
            self.docs_path / "usage_and_configuration" / "the_basics.md",
            self.docs_path / "guides" / "using_black_with_jupyter_notebooks.md",
        )

        self.version_override = version_override

        LOG.debug(self)

    def __str__(self) -> str:
        next_vesion = self.get_next_version()
        if self.version_override:
            next_vesion += " (overridden)"

        return f"""\
> SourceFiles ENV:
  Repo path: {self.black_repo_path}
  CHANGES.md path: {self.changes_path}
  Docs path: {self.docs_path}
  Current version: {self.get_current_version()}
  Next version: {next_vesion}
"""

    def get_current_version(self) -> str | None:
        """Get the latest git (version) tag as latest version"""
        versions = get_git_tags()
        if versions:
            return versions[0]
        return None

    def get_next_version(self) -> str:
        """Determine the next version number based off the current year and month"""
        if self.version_override:
            return self.version_override

        base_calver = datetime.today().strftime("%y.%m")
        base_calver = f"{Version(base_calver)}."  # Remove leading 0

        current_version = self.get_current_version()
        if not current_version or not current_version.startswith(base_calver):
            return f"{base_calver}0"
        return f"{base_calver}{Version(current_version).micro + 1}"

    def get_prerelease_version(self) -> str:
        parts = self.get_next_version().split(".", maxsplit=2)
        base = f"{parts[0]}.{parts[1]}a"
        LOG.debug(f"Base version: {base}")

        last_prerelease = next(
            (version for version in get_git_tags(True) if version.startswith(base)),
            None,
        )
        if not last_prerelease:
            LOG.debug("No previous prerelease, defaulting to 1")
            return f"{base}1"
        LOG.debug("Found previous prerelease")
        pre = Version(last_prerelease).pre
        return f"{base}{pre[1] + 1 if pre else 1}"

    def update_repo_for_release(self) -> int:
        """Update CHANGES.md + doc files ready for release"""
        LOG.info(f"Current version detected to be {self.get_current_version()}")
        LOG.info(f"Next version will be {self.get_next_version()}")
        LOG.info("")

        self.update_version_in_docs()
        self.cleanup_changes_template_for_release()

        LOG.info("")
        LOG.info("Successfully completed updating repo for release!")

        return 0  # return 0 if no exceptions hit

    def update_version_in_docs(self) -> None:
        current_version = self.get_current_version()
        if not current_version:
            return
        next_version = self.get_next_version()

        for doc_path in self.version_doc_paths:
            LOG.info(f"Updating Black version to {next_version} in {doc_path}")

            with doc_path.open("r", encoding="utf-8") as dfp:
                doc_string = dfp.read()

            next_version_doc = doc_string.replace(current_version, next_version)

            with doc_path.open("w", encoding="utf-8") as dfp:
                dfp.write(next_version_doc)

            LOG.debug(
                f"Finished updating Black version to {next_version} in {doc_path}"
            )

    def cleanup_changes_template_for_release(self) -> None:
        LOG.info(f"Cleaning up {self.changes_path}")

        with self.changes_path.open("r", encoding="utf-8") as cfp:
            changes_string = cfp.read()

        next_version = self.get_next_version()
        # Change Unreleased to next version
        changes_string = changes_string.replace(
            "## Unreleased", f"## Version {next_version}"
        )

        # Remove all comments
        changes_string = re.sub(r"(?m)^<!--(?>(?:.|\n)*?-->)\n+", "", changes_string)

        # Remove empty subheadings
        changes_string = re.sub(r"(?m)^###.+\n+(?=#)", "", changes_string)

        with self.changes_path.open("w", encoding="utf-8") as cfp:
            cfp.write(changes_string)

        LOG.debug(f"Finished cleaning up {self.changes_path}")

    def add_template_to_changes(self) -> int:
        """Add the template to CHANGES.md if it does not exist"""
        LOG.debug(f"Adding template to {self.changes_path}")

        with self.changes_path.open("r", encoding="utf-8") as cfp:
            changes_string = cfp.read()

        if "## Unreleased" in changes_string:
            LOG.error(f"{self.changes_path} already has unreleased template")
            return 1

        templated_changes_string = changes_string.replace(
            "# Change Log\n", f"# Change Log\n\n{NEW_VERSION_CHANGELOG_TEMPLATE}"
        )

        with self.changes_path.open("w", encoding="utf-8") as cfp:
            cfp.write(templated_changes_string)

        LOG.info(f"Added template to {self.changes_path}")
        return 0

    def get_changelog(self) -> str | None:
        with self.changes_path.open("r", encoding="utf-8") as cfp:
            changes_string = cfp.read()

        versions = changes_string.split("\n## ", maxsplit=2)
        if len(versions) < 2:
            LOG.error("Not enough headings in changelog")
            return None

        heading_split = versions[1].split("\n", maxsplit=1)
        if len(heading_split) < 2:
            LOG.error("Not enough lines in section")
            return None

        LOG.info(f"Changelog for {heading_split[0]}")
        return heading_split[1].strip()


def _handle_debug(debug: bool) -> None:
    """Turn on debugging if asked, otherwise default to INFO"""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s: %(message)s (%(filename)s:%(lineno)d)",
        level=log_level,
    )
    LOG.debug(f"Log level: {logging.getLevelName(log_level)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Verbose debug output, even if a command disables it",
    )

    subparsers = parser.add_subparsers(dest="command")

    def add_parser(name: str, help: str) -> argparse.ArgumentParser:
        return subparsers.add_parser(name, help=help, description=help)

    add_parser("prepare", help="Prepare a release").add_argument(
        "version", type=str, nargs="?", help="Override the next version"
    )
    add_parser("add", help="Add the Unreleased template to CHANGES.md")
    add_parser(
        "prerelease",
        help="Returns the next prerelease version for the given stable version",
    ).add_argument("version", type=str, help="The stable version")
    add_parser("version", help="Returns the next version number")
    add_parser("changes", help="Returns the latest changelog")

    args = parser.parse_args()
    return args


def main() -> int:
    args = parse_args()

    if (args.command == "prepare" or args.command == "add") or args.debug:
        _handle_debug(args.debug)

    # Need parent.parent cause script is in scripts/ directory
    sf = SourceFiles(
        Path(__file__).parent.parent, args.version if "version" in args else None
    )

    LOG.debug(f"Running command {args.command}")

    match args.command:
        case "prepare":
            return sf.update_repo_for_release()
        case "add":
            return sf.add_template_to_changes()
        case "prerelease":
            print(sf.get_prerelease_version())
            return 0
        case "version":
            print(sf.get_next_version())
            return 0
        case "changes":
            changes = sf.get_changelog()
            if not changes:
                return 1
            print(changes)
            return 0

    LOG.error(f"Unknown command: {args.command}")
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
