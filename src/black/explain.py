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

    def add_decision(self, path: Path, decision: Decision) -> None:
        """Add an entry from a structured Decision."""
        if not self.enabled:
            return
        self.entries.append(decision.to_entry(path))

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


# ============================================================================
# Structured Decision + Ruleset Evaluator
# ============================================================================


@dataclass(frozen=True)
class Decision:
    """
    A structured decision for a path during file discovery.

    Shows both reason_code (for ignored paths) and provenance (for included paths).
    """

    status: Literal["included", "ignored"]
    reason_code: str = ""  # ExplainReason value (for ignored)
    provenance: str = ""  # ExplainProvenance value (for included)
    detail: str = ""
    source: str = ""

    def is_included(self) -> bool:
        return self.status == "included"

    def is_ignored(self) -> bool:
        return self.status == "ignored"

    @property
    def code(self) -> str:
        """Return the primary code (reason_code for ignored, provenance for included)."""
        return self.provenance if self.is_included() else self.reason_code

    def to_entry(self, path: Path) -> ExplainEntry:
        """Convert to ExplainEntry (uses primary code)."""
        return ExplainEntry(
            path=path,
            status=self.status,
            code=self.code,
            detail=self.detail,
            source=self.source,
        )

    def to_dict_full(self) -> dict:
        """Convert to dict with both reason_code and provenance."""
        return {
            "status": self.status,
            "reason_code": self.reason_code,
            "provenance": self.provenance,
            "code": self.code,
            "detail": self.detail,
            "source": self.source,
        }


@dataclass(frozen=True)
class EvalContext:
    """Context for evaluating path decisions."""

    root: Path
    include_pattern: "Pattern[str] | None" = None
    exclude_pattern: "Pattern[str] | None" = None
    extend_exclude_pattern: "Pattern[str] | None" = None
    force_exclude_pattern: "Pattern[str] | None" = None
    gitignore_dict: dict[Path, "GitIgnoreSpec"] | None = None
    is_stdin: bool = False
    stdin_filename: str | None = None
    jupyter_deps_available: bool = True

    @classmethod
    def from_cli(
        cls,
        root: Path,
        include: "Pattern[str] | None",
        exclude: "Pattern[str] | None",
        extend_exclude: "Pattern[str] | None",
        force_exclude: "Pattern[str] | None",
        gitignore_dict: dict[Path, "GitIgnoreSpec"] | None,
        is_stdin: bool = False,
        stdin_filename: str | None = None,
        jupyter_deps_available: bool = True,
    ) -> "EvalContext":
        """Create from CLI parameters."""
        return cls(
            root=root,
            include_pattern=include,
            exclude_pattern=exclude,
            extend_exclude_pattern=extend_exclude,
            force_exclude_pattern=force_exclude,
            gitignore_dict=gitignore_dict,
            is_stdin=is_stdin,
            stdin_filename=stdin_filename,
            jupyter_deps_available=jupyter_deps_available,
        )


@dataclass(frozen=True)
class Rule:
    """
    A single rule that evaluates a path.

    The evaluate() method checks conditions and returns Decision if rule matches,
    or None if not applicable. Rules are evaluated in order by RulesetEvaluator.
    """

    name: str = "rule"
    reason_code: str = ""  # ExplainReason value (for ignored)
    provenance: str = ""  # ExplainProvenance value (for included)
    status: Literal["included", "ignored"] = "ignored"
    detail: str = ""
    source: str = ""

    def evaluate(self, path: Path, ctx: EvalContext) -> Decision | None:
        """
        Evaluate path against this rule.

        Returns Decision if rule matches, None if not applicable.
        Subclasses override this to add actual condition checking.
        """
        return Decision(
            status=self.status,
            reason_code=self.reason_code,
            provenance=self.provenance,
            detail=self.detail,
            source=self.source,
        )


# Context-aware rules with actual condition checking


@dataclass(frozen=True)
class GitignoreRule(Rule):
    """Rule that checks if path matches any .gitignore pattern."""

    name: str = "gitignore_match"
    reason_code: str = ExplainReason.GITIGNORE_MATCH.value
    status: Literal["included", "ignored"] = "ignored"
    detail: str = "matches .gitignore pattern"

    def evaluate(self, path: Path, ctx: EvalContext) -> Decision | None:
        if not ctx.gitignore_dict:
            return None
        from black.files import _path_is_ignored, best_effort_relative_path

        try:
            root_relative = best_effort_relative_path(path, ctx.root).as_posix()
            if _path_is_ignored(root_relative, ctx.root, ctx.gitignore_dict):
                source = ""
                for gitignore_path in ctx.gitignore_dict.keys():
                    if path.is_relative_to(gitignore_path):
                        source = str(gitignore_path / ".gitignore")
                        break
                return Decision(
                    status="ignored",
                    reason_code=self.reason_code,
                    detail=self.detail,
                    source=source,
                )
        except Exception:
            pass
        return None


@dataclass(frozen=True)
class ExcludePatternRule(Rule):
    """Rule that checks if path matches an exclude pattern."""

    pattern_name: str = "--exclude"
    pattern_attr: str = "exclude_pattern"

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", f"{self.pattern_name}_match")
        object.__setattr__(self, "reason_code", ExplainReason.EXCLUDE_REGEX.value)
        object.__setattr__(self, "status", "ignored")
        object.__setattr__(self, "detail", f"matches {self.pattern_name}")
        object.__setattr__(self, "source", self.pattern_name)

    def evaluate(self, path: Path, ctx: EvalContext) -> Decision | None:
        from black.files import path_is_excluded, best_effort_relative_path

        pattern = getattr(ctx, self.pattern_attr, None)
        if not pattern:
            return None
        try:
            root_relative = best_effort_relative_path(path, ctx.root).as_posix()
            root_relative = "/" + root_relative
            if path.is_dir():
                root_relative += "/"
            if path_is_excluded(root_relative, pattern):
                return Decision(
                    status="ignored",
                    reason_code=self.reason_code,
                    detail=self.detail,
                    source=self.source,
                )
        except Exception:
            pass
        return None


@dataclass(frozen=True)
class ForceExcludeRule(Rule):
    """Rule that checks force-exclude pattern."""

    name: str = "force_exclude_match"
    reason_code: str = ExplainReason.FORCE_EXCLUDE_REGEX.value
    status: Literal["included", "ignored"] = "ignored"
    detail: str = "matches --force-exclude"
    source: str = "--force-exclude"

    def evaluate(self, path: Path, ctx: EvalContext) -> Decision | None:
        from black.files import path_is_excluded, best_effort_relative_path

        if not ctx.force_exclude_pattern:
            return None
        try:
            root_relative = best_effort_relative_path(path, ctx.root).as_posix()
            root_relative = "/" + root_relative
            if path.is_dir():
                root_relative += "/"
            if path_is_excluded(root_relative, ctx.force_exclude_pattern):
                return Decision(
                    status="ignored",
                    reason_code=self.reason_code,
                    detail=self.detail,
                    source=self.source,
                )
        except Exception:
            pass
        return None


@dataclass(frozen=True)
class StdinForceExcludeRule(Rule):
    """Rule that checks if stdin-filename matches force-exclude."""

    name: str = "stdin_force_exclude"
    reason_code: str = ExplainReason.STDIN_FORCE_EXCLUDE.value
    status: Literal["included", "ignored"] = "ignored"
    detail: str = "--stdin-filename matches --force-exclude"
    source: str = "--force-exclude"

    def evaluate(self, path: Path, ctx: EvalContext) -> Decision | None:
        from black.files import path_is_excluded

        if not ctx.is_stdin or not ctx.stdin_filename or not ctx.force_exclude_pattern:
            return None
        if path_is_excluded(ctx.stdin_filename, ctx.force_exclude_pattern):
            return Decision(
                status="ignored",
                reason_code=self.reason_code,
                detail=self.detail,
                source=self.source,
            )
        return None


@dataclass(frozen=True)
class CannotStatRule(Rule):
    """Rule that checks if path cannot be stat'd or resolves outside root."""

    name: str = "cannot_stat"
    reason_code: str = ExplainReason.CANNOT_STAT.value
    status: Literal["included", "ignored"] = "ignored"
    detail: str = "cannot stat or resolves outside root"
    source: str = "path resolution"

    def evaluate(self, path: Path, ctx: EvalContext) -> Decision | None:
        from black.files import _cached_resolve

        try:
            resolved = _cached_resolve(path)
            resolved.relative_to(ctx.root)
        except (OSError, ValueError):
            return Decision(
                status="ignored",
                reason_code=self.reason_code,
                detail=self.detail,
                source=self.source,
            )
        return None


@dataclass(frozen=True)
class JupyterDepsMissingRule(Rule):
    """Rule that checks if .ipynb but jupyter deps not available."""

    name: str = "jupyter_deps_missing"
    reason_code: str = ExplainReason.JUPYTER_DEPS_MISSING.value
    status: Literal["included", "ignored"] = "ignored"
    detail: str = ".ipynb file but jupyter dependencies not installed"
    source: str = "--ipynb requires jupyter"

    def evaluate(self, path: Path, ctx: EvalContext) -> Decision | None:
        if path.suffix == ".ipynb" and not ctx.jupyter_deps_available:
            return Decision(
                status="ignored",
                reason_code=self.reason_code,
                detail=self.detail,
                source=self.source,
            )
        return None


@dataclass(frozen=True)
class NotIncludedRule(Rule):
    """Rule that checks if file doesn't match include pattern."""

    name: str = "not_included"
    reason_code: str = ExplainReason.NOT_INCLUDED.value
    status: Literal["included", "ignored"] = "ignored"
    detail: str = "does not match --include pattern"
    source: str = "--include"

    def evaluate(self, path: Path, ctx: EvalContext) -> Decision | None:
        from black.files import best_effort_relative_path

        if not ctx.include_pattern:
            return None  # Empty include means all files included
        if not path.is_file():
            return None
        try:
            root_relative = best_effort_relative_path(path, ctx.root).as_posix()
            root_relative = "/" + root_relative
            if not ctx.include_pattern.search(root_relative):
                return Decision(
                    status="ignored",
                    reason_code=self.reason_code,
                    detail=self.detail,
                    source=self.source,
                )
        except Exception:
            pass
        return None


@dataclass(frozen=True)
class ProvenanceRule(Rule):
    """Rule that returns included with a provenance type (default pass-through)."""

    name: str = "provenance"
    provenance: str = ExplainProvenance.DISCOVERED_VIA_WALK.value
    status: Literal["included", "ignored"] = "included"
    detail: str = "discovered via directory walk"
    source: str = "--include pattern"

    def evaluate(self, path: Path, ctx: EvalContext) -> Decision | None:
        return Decision(
            status="included",
            provenance=self.provenance,
            detail=self.detail,
            source=self.source,
        )


class RulesetEvaluator:
    """
    Evaluates a path against a set of rules and returns a Decision.

    Rules are evaluated in order. First rule whose evaluate() returns non-None wins.
    If no rule matches, defaults to included with DISCOVERED_VIA_WALK provenance.
    """

    def __init__(self, rules: list[Rule] | None = None):
        self.rules = rules or []

    def add_rule(self, rule: Rule) -> None:
        """Add a rule to the evaluator."""
        self.rules.append(rule)

    def evaluate(self, path: Path, ctx: EvalContext) -> Decision:
        """
        Evaluate path against all rules. Returns first matching decision.

        Rules are evaluated in order. First rule whose evaluate() returns non-None wins.
        """
        for rule in self.rules:
            decision = rule.evaluate(path, ctx)
            if decision is not None:
                return decision
        # Default: include with discovered_via_walk provenance
        return Decision(
            status="included",
            reason_code=ExplainProvenance.DISCOVERED_VIA_WALK.value,
            detail="discovered via directory walk",
            source="--include pattern",
        )

    @classmethod
    def default_for_discovery(cls) -> "RulesetEvaluator":
        """
        Create evaluator with default rules for file discovery.

        Order matters: more specific exclusions first, then include check, then default.
        """
        return cls(
            [
                StdinForceExcludeRule(),
                GitignoreRule(),
                ExcludePatternRule(pattern_name="--exclude", pattern_attr="exclude_pattern"),
                ExcludePatternRule(pattern_name="--extend-exclude", pattern_attr="extend_exclude_pattern"),
                ForceExcludeRule(),
                CannotStatRule(),
                JupyterDepsMissingRule(),
                NotIncludedRule(),
                ProvenanceRule(),  # Final: default include
            ]
        )
