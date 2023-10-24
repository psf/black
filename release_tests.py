#!/usr/bin/env python3

import unittest
from pathlib import Path
from shutil import copy, rmtree
from tempfile import TemporaryDirectory
from typing import Any
from unittest.mock import Mock, patch

from release import SourceFiles, int_calver


class FakeDateTime:
    """Used to mock the date to test generating next calver function"""

    def today(self, *args: Any, **kwargs: Any) -> "FakeDateTime":
        return FakeDateTime()

    # Add leading 0 on purpose to ensure we remove it
    def strftime(self, *args: Any, **kwargs: Any) -> str:
        return "69.01"


class TestRelease(unittest.TestCase):
    def setUp(self) -> None:
        # We only test on >= 3.12
        self.tempdir = TemporaryDirectory(delete=False)  # type: ignore
        self.tempdir_path = Path(self.tempdir.name)
        self.sf_real_black_repo = SourceFiles(Path(__file__).parent)
        self.sf = SourceFiles(self.tempdir_path)
        self._make_fake_black_repo()
        # check we have a repo + changes file
        self.assertTrue(self.sf.changes_path.exists())

    def _make_fake_black_repo(self) -> None:
        copy(self.sf_real_black_repo.changes_path, self.sf.changes_path)
        for idx, doc_path in enumerate(self.sf.version_doc_paths):
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            copy(self.sf_real_black_repo.version_doc_paths[idx], doc_path)

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

    def test_int_calver(self) -> None:
        first_month_release = int_calver("69.1.0")
        second_month_release = int_calver("69.1.1")
        self.assertEqual(6910, first_month_release)
        self.assertEqual(6911, second_month_release)
        self.assertTrue(first_month_release < second_month_release)


if __name__ == "__main__":
    unittest.main()
