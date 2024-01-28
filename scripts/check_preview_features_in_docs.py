"""

Check that the lists of preview features in the docs are up to date.

"""

import re
import sys
from itertools import islice
from pathlib import Path
from typing import Sequence, Set

from black.mode import UNSTABLE_FEATURES, Preview

DOCS_PATH = Path("docs/the_black_code_style/future_style.md")


def check_feature_list(
    lines: Sequence[str], expected_feature_names: Set[str], label: str
) -> bool:
    start_index = lines.index(f"(labels/{label}-features)=\n")
    if start_index == -1:
        print(
            f"Could not find the {label} features list in the docs. Ensure the"
            " preview-features label is present.",
            file=sys.stderr,
        )
        return False
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
        print(
            f"The following features should not be in the list of {label} features:",
            file=sys.stderr,
        )
        for feature in sorted(seen_preview_feature_names - expected_feature_names):
            print(f"- `{feature}`", file=sys.stderr)
        print(
            f"Please remove them from the {label}-features label in {DOCS_PATH}",
            file=sys.stderr,
        )
        return False
    elif expected_feature_names - seen_preview_feature_names:
        print(
            f"The following features are missing from the list of {label} features:",
            file=sys.stderr,
        )
        for feature in sorted(expected_feature_names - seen_preview_feature_names):
            print(f"- `{feature}`", file=sys.stderr)
        print(
            f"Please document them under the {label}-features label in {DOCS_PATH}",
            file=sys.stderr,
        )
        return False
    else:
        return True


def main() -> int:
    with DOCS_PATH.open(encoding="utf-8") as f:
        future_style = f.readlines()
    preview_success = check_feature_list(
        future_style,
        {feature.name for feature in set(Preview) - UNSTABLE_FEATURES},
        "preview",
    )
    unstable_success = check_feature_list(
        future_style, {feature.name for feature in UNSTABLE_FEATURES}, "unstable"
    )
    if preview_success and unstable_success:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
