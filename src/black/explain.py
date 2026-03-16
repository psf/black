"""
Explain mode for Black file discovery.

Provides reason codes and provenance types for why paths are included or ignored.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Literal


class ExplainReason(Enum):
    """Reason codes for why a path was ignored."""

    # Gitignore
    GITIGNORE_MATCH = "GITIGNORE_MATCH"

    # Exclude patterns
    EXCLUDE_REGEX = "EXCLUDE_REGEX"
    EXTEND_EXCLUDE_REGEX = "EXTEND_EXCLUDE_REGEX"
    FORCE_EXCLUDE_REGEX = "FORCE_EXCLUDE_REGEX"
    STDIN_FORCE_EXCLUDE = "STDIN_FORCE_EXCLUDE"

    # Path issues
    CANNOT_STAT = "CANNOT_STAT"
    SYMLINK_OUTSIDE_ROOT = "SYMLINK_OUTSIDE_ROOT"
    NOT_FILE_OR_DIR = "NOT_FILE_OR_DIR"
    INVALID_PATH = "INVALID_PATH"

    # Jupyter
    JUPYTER_DEPS_MISSING = "JUPYTER_DEPS_MISSING"

    # Include pattern not matched
    NOT_INCLUDED = "NOT_INCLUDED"

    # Explicit skip (for future use)
    EXPLICIT_SKIP = "EXPLICIT_SKIP"


class ExplainProvenance(Enum):
    """Provenance types for why a path was included."""

    EXPLICIT_FILE = "EXPLICIT_FILE"
    EXPLICIT_STDIN = "EXPLICIT_STDIN"
    EXPLICIT_STDIN_FILENAME = "EXPLICIT_STDIN_FILENAME"
    DISCOVERED_VIA_WALK = "DISCOVERED_VIA_WALK"


@dataclass(frozen=True)
class ExplainEntry:
    """A single explain entry for a path decision."""

    path: Path
    status: Literal["included", "ignored"]
    code: str  # ExplainReason value or ExplainProvenance value
    detail: str = ""  # Human-readable detail
    source: str = ""  # Source of decision (e.g., gitignore path, regex pattern)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output."""
        return {
            "path": str(self.path),
            "status": self.status,
            "code": self.code,
            "detail": self.detail,
            "source": self.source,
        }

    def to_text(self) -> str:
        """Convert to human-readable text line."""
        prefix = "+" if self.status == "included" else "-"
        parts = [f"{prefix} {self.path} [{self.code}]"]
        if self.detail:
            parts.append(f": {self.detail}")
        if self.source:
            parts.append(f" (source: {self.source})")
        return "".join(parts)


@dataclass
class ExplainReport:
    """Collects and formats explain entries."""

    entries: list[ExplainEntry] = field(default_factory=list)
    enabled: bool = False
    format: Literal["text", "json", "jsonl"] = "text"
    show: Literal["all", "included", "ignored"] = "all"
    limit: int | None = None
    simulate: bool = False

    def add_included(
        self,
        path: Path,
        provenance: ExplainProvenance,
        detail: str = "",
        source: str = "",
    ) -> None:
        """Add an included path entry."""
        if not self.enabled:
            return
        self.entries.append(
            ExplainEntry(
                path=path,
                status="included",
                code=provenance.value,
                detail=detail,
                source=source,
            )
        )

    def add_ignored(
        self,
        path: Path,
        reason: ExplainReason,
        detail: str = "",
        source: str = "",
    ) -> None:
        """Add an ignored path entry."""
        if not self.enabled:
            return
        self.entries.append(
            ExplainEntry(
                path=path,
                status="ignored",
                code=reason.value,
                detail=detail,
                source=source,
            )
        )

    def get_entries(self) -> Sequence[ExplainEntry]:
        """Get filtered and limited entries."""
        result = self.entries
        if self.show == "included":
            result = [e for e in result if e.status == "included"]
        elif self.show == "ignored":
            result = [e for e in result if e.status == "ignored"]
        if self.limit is not None:
            result = result[: self.limit]
        return result

    def render(self) -> str:
        """Render the report according to format."""
        entries = self.get_entries()
        if self.format == "json":
            return json.dumps(
                {"entries": [e.to_dict() for e in entries]}, indent=2
            )
        elif self.format == "jsonl":
            return "\n".join(json.dumps(e.to_dict()) for e in entries)
        else:  # text
            lines = [e.to_text() for e in entries]
            summary = self._summary()
            if summary:
                lines.append("")
                lines.append(summary)
            return "\n".join(lines)

    def _summary(self) -> str:
        """Generate summary line."""
        included = sum(1 for e in self.entries if e.status == "included")
        ignored = sum(1 for e in self.entries if e.status == "ignored")
        return f"Summary: {included} included, {ignored} ignored"

    def print_to_stdout(self) -> None:
        """Print to stdout via black.output."""
        from black.output import out

        text = self.render()
        if text:
            out(text, bold=False)


# All reason codes as a list (for documentation / file export)
ALL_REASON_CODES: list[str] = [r.value for r in ExplainReason]

# All provenance types as a list (for documentation / file export)
ALL_PROVENANCE_TYPES: list[str] = [p.value for p in ExplainProvenance]


def export_explain_schema() -> dict:
    """Export all reason codes and provenance types as a schema dict."""
    return {
        "reason_codes": [
            {"code": r.value, "description": _reason_description(r)}
            for r in ExplainReason
        ],
        "provenance_types": [
            {"type": p.value, "description": _provenance_description(p)}
            for p in ExplainProvenance
        ],
    }


def _reason_description(r: ExplainReason) -> str:
    """Human-readable description for a reason code."""
    descriptions = {
        ExplainReason.GITIGNORE_MATCH: "Path matched a .gitignore pattern",
        ExplainReason.EXCLUDE_REGEX: "Path matched --exclude regular expression",
        ExplainReason.EXTEND_EXCLUDE_REGEX: "Path matched --extend-exclude regular expression",
        ExplainReason.FORCE_EXCLUDE_REGEX: "Path matched --force-exclude regular expression",
        ExplainReason.STDIN_FORCE_EXCLUDE: "--stdin-filename matched --force-exclude",
        ExplainReason.CANNOT_STAT: "Path could not be stat'd or resolved",
        ExplainReason.SYMLINK_OUTSIDE_ROOT: "Symlink resolves outside project root",
        ExplainReason.NOT_FILE_OR_DIR: "Path is neither file nor directory",
        ExplainReason.INVALID_PATH: "Path is not a valid source (neither file, dir, nor stdin)",
        ExplainReason.JUPYTER_DEPS_MISSING: "Jupyter dependencies not installed for .ipynb",
        ExplainReason.NOT_INCLUDED: "File does not match --include pattern",
        ExplainReason.EXPLICIT_SKIP: "Explicitly skipped",
    }
    return descriptions.get(r, r.value)


def _provenance_description(p: ExplainProvenance) -> str:
    """Human-readable description for a provenance type."""
    descriptions = {
        ExplainProvenance.EXPLICIT_FILE: "Explicit file path argument",
        ExplainProvenance.EXPLICIT_STDIN: "Stdin input (via -)",
        ExplainProvenance.EXPLICIT_STDIN_FILENAME: "Stdin with --stdin-filename",
        ExplainProvenance.DISCOVERED_VIA_WALK: "Discovered via directory walk",
    }
    return descriptions.get(p, p.value)


def save_explain_schema_to_file(path: Path) -> None:
    """Save the explain schema to a JSON file."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(export_explain_schema(), f, indent=2)
