#!/usr/bin/env python3

import unittest
from pathlib import Path
from shutil import rmtree
from tempfile import TemporaryDirectory
from typing import Any
from unittest.mock import Mock, patch

from release import SourceFiles, is_valid_version  # type: ignore


class FakeDateTime:
    """Used to mock the date to test generating next calver function"""

    def today(*args: Any, **kwargs: Any) -> "FakeDateTime":  # noqa: B902
        return FakeDateTime()

    # Add leading 0 on purpose to ensure we remove it
    def strftime(*args: Any, **kwargs: Any) -> str:  # noqa: B902
        return "69.01"


class TestRelease(unittest.TestCase):
    def setUp(self) -> None:
        # We only test on >= 3.12
        self.tempdir = TemporaryDirectory(delete=False)  # type: ignore
        self.tempdir_path = Path(self.tempdir.name)
        self.sf = SourceFiles(self.tempdir_path, None)

    def tearDown(self) -> None:
        rmtree(self.tempdir.name)
        return super().tearDown()

    @patch("release.get_git_tags")
    def test_get_current_version(self, mocked_git_tags: Mock) -> None:
        mocked_git_tags.return_value = ["69.1.1", "69.1.0", "2.2.0", "1.1.0"]
        self.assertEqual("69.1.1", self.sf.get_current_version())

    @patch("release.get_git_tags")
    @patch("release.datetime", FakeDateTime)
    def test_get_next_version(self, mocked_git_tags: Mock) -> None:
        # test we handle no prior releases
        mocked_git_tags.return_value = []
        self.assertEqual(
            "69.1.0",
            self.sf.get_next_version(),
            "Unable to get correct next version with no git tags",
        )

        # test we handle first release in a month
        mocked_git_tags.return_value = ["2.2.0", "1.1.0"]
        self.assertEqual(
            "69.1.0",
            self.sf.get_next_version(),
            "Unable to get correct version for first release in a month",
        )

        # test we handle multiple releases in a month
        mocked_git_tags.return_value = ["69.1.1", "69.1.0", "2.2.0", "1.1.0"]
        self.assertEqual(
            "69.1.2",
            self.sf.get_next_version(),
            "Unable to get correct version with 2 previous versions released this"
            " month",
        )

    @patch("release.get_git_tags")
    @patch("release.datetime", FakeDateTime)
    def test_get_prerelease_version(self, mocked_git_tags: Mock) -> None:
        with patch.object(self.sf, "version_override", "69.2.0"):
            # test we handle no prior releases
            mocked_git_tags.return_value = []
            self.assertEqual(
                "69.2a1",
                self.sf.get_prerelease_version(),
                "Unable to get correct prerelease version with no git tags",
            )

            # test we handle second release in a year
            mocked_git_tags.return_value = ["69.1.0"]
            self.assertEqual(
                "69.2a1",
                self.sf.get_prerelease_version(),
                "Unable to get correct prerelease version for second release in a year",
            )

            # test we handle multiple prereleases in a month
            mocked_git_tags.return_value = ["69.2a2", "69.2a1", "69.1.0"]
            self.assertEqual(
                "69.2a3",
                self.sf.get_prerelease_version(),
                "Unable to get correct prerelease version with 2 previous prereleases"
                " this month",
            )

    def test_is_valid_version(self) -> None:
        self.assertTrue(is_valid_version("1.2.3", True))
        self.assertTrue(is_valid_version("1.2a1", True))
        self.assertFalse(is_valid_version("stable", True))
        self.assertFalse(is_valid_version("1.2a1", False))


if __name__ == "__main__":
    unittest.main()
