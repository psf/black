"""Tests for release workflow configuration."""

from pathlib import Path

PUBLISH_BINARIES_WORKFLOW = (
    Path(__file__).parent.parent / ".github/workflows/publish_binaries.yml"
)
RELEASE_PROCESS_DOC = (
    Path(__file__).parent.parent / "docs/contributing/release_process.md"
)


def test_publish_binaries_uploads_before_release_is_published() -> None:
    workflow = PUBLISH_BINARIES_WORKFLOW.read_text(encoding="utf-8")
    assert "types: [created]" in workflow
    assert "types: [published]" not in workflow


def test_release_process_documents_draft_then_publish_flow() -> None:
    release_process = RELEASE_PROCESS_DOC.read_text(encoding="utf-8")
    assert "Save the release as a draft" in release_process
    assert "the draft release" in release_process.lower()
    assert "immutable releases" in release_process.lower()
