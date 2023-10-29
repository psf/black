#!/usr/bin/env python3

import unittest
from pathlib import Path
from shutil import rmtree
from tempfile import TemporaryDirectory
from typing import Any
from unittest.mock import Mock, patch

from release import SourceFiles, tuple_calver  # type: ignore


class FakeDateTime:
    """Used to mock the date to test generating next calver function"""

    def today(*args: Any, **kwargs: Any) -> "FakeDateTime":  # noqa
        return FakeDateTime()

    # Add leading 0 on purpose to ensure we remove it
    def strftime(*args: Any, **kwargs: Any) -> str:  # noqa
        return "69.01"


class TestRelease(unittest.TestCase):
    def setUp(self) -> None:
        # We only test on >= 3.12
        self.tempdir = TemporaryDirectory(delete=False)  # type: ignore
        self.tempdir_path = Path(self.tempdir.name)
        self.sf = SourceFiles(self.tempdir_path)

    def tearDown(self) -> None:
        rmtree(self.tempdir.name)
        return super().tearDown()

    @patch("release.get_git_tags")
    def test_get_current_version(self, mocked_git_tags: Mock) -> None:
        mocked_git_tags.return_value = ["1.1.0", "69.1.0", "69.1.1", "2.2.0"]
        self.assertEqual("69.1.1", self.sf.get_current_version())

    @patch("release.get_git_tags")
    @patch("release.datetime", FakeDateTime)
    def test_get_next_version(self, mocked_git_tags: Mock) -> None:
        # test we handle no args
        mocked_git_tags.return_value = []
        self.assertEqual(
            "69.1.0",
            self.sf.get_next_version(),
            "Unable to get correct next version with no git tags",
        )

        # test we handle
        mocked_git_tags.return_value = ["1.1.0", "69.1.0", "69.1.1", "2.2.0"]
        self.assertEqual(
            "69.1.2",
            self.sf.get_next_version(),
            "Unable to get correct version with 2 previous versions released this"
            " month",
        )

    def test_tuple_calver(self) -> None:
        first_month_release = tuple_calver("69.1.0")
        second_month_release = tuple_calver("69.1.1")
        self.assertEqual((69, 1, 0), first_month_release)
        self.assertEqual((0, 0, 0), tuple_calver("69.1.1a0"))  # Hack for alphas/betas
        self.assertTrue(first_month_release < second_month_release)


if __name__ == "__main__":
    unittest.main()
