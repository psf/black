"""

Test that the docs are up to date.

"""

import re
from collections.abc import Sequence
from itertools import islice
from pathlib import Path
from typing import Optional

import pytest

from black.mode import UNSTABLE_FEATURES, Preview

DOCS_PATH = Path("docs/the_black_code_style/future_style.md")


def check_feature_list(
    lines: Sequence[str], expected_feature_names: set[str], label: str
) -> Optional[str]:
    start_index = lines.index(f"(labels/{label}-features)=\n")
    if start_index == -1:
        return (
            f"Could not find the {label} features list in {DOCS_PATH}. Ensure the"
            " preview-features label is present."
        )
    num_blank_lines_seen = 0
    seen_preview_feature_names = set()
    for line in islice(lines, start_index + 1, None):
        if not line.strip():
            num_blank_lines_seen += 1
            if num_blank_lines_seen == 3:
                break
            continue
        if line.startswith("- "):
            match = re.search(r"^- `([a-z\d_]+)`", line)
            if match:
                seen_preview_feature_names.add(match.group(1))

    if seen_preview_feature_names - expected_feature_names:
        extra = ", ".join(sorted(seen_preview_feature_names - expected_feature_names))
        return (
            f"The following features should not be in the list of {label} features:"
            f" {extra}. Please remove them from the {label}-features label in"
            f" {DOCS_PATH}"
        )
    elif expected_feature_names - seen_preview_feature_names:
        missing = ", ".join(sorted(expected_feature_names - seen_preview_feature_names))
        return (
            f"The following features are missing from the list of {label} features:"
            f" {missing}. Please document them under the {label}-features label in"
            f" {DOCS_PATH}"
        )
    else:
        return None


def test_feature_lists_are_up_to_date() -> None:
    repo_root = Path(__file__).parent.parent
    if not (repo_root / "docs").exists():
        pytest.skip("docs not found")
    with (repo_root / DOCS_PATH).open(encoding="utf-8") as f:
        future_style = f.readlines()
    preview_error = check_feature_list(
        future_style,
        {feature.name for feature in set(Preview) - UNSTABLE_FEATURES},
        "preview",
    )
    assert preview_error is None, preview_error
    unstable_error = check_feature_list(
        future_style, {feature.name for feature in UNSTABLE_FEATURES}, "unstable"
    )
    assert unstable_error is None, unstable_error
