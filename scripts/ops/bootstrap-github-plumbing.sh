#!/usr/bin/env bash
set -euo pipefail

# Bootstrap GitHub labels & milestones for this repo.
# - Idempotent: upserts labels and milestones
# - Dry-run by default; use --apply to make changes
# - Requires: gh (GitHub CLI), GH_TOKEN auth
#
# Usage:
#   bash scripts/ops/bootstrap-github-plumbing.sh OWNER/REPO           # dry-run
#   bash scripts/ops/bootstrap-github-plumbing.sh OWNER/REPO --apply   # apply
#
# Optional env for milestone due dates (ISO 8601 or YYYY-MM-DD).
#   SPRINT1_DUE="2025-11-07"
#   SPRINT2_DUE="2025-12-05"
#   SPRINT3_DUE="2026-01-09"
#
# Exit codes:
#   0 success
#   2 missing deps or not authenticated
#   3 usage error

REPO="${1:-}"
MODE="${2:-}"
if [[ -z "$REPO" ]]; then
  echo "Usage: $0 OWNER/REPO [--apply]" >&2
  exit 3
fi

APPLY=false
if [[ "${MODE:-}" == "--apply" ]]; then
  APPLY=true
elif [[ -n "${MODE:-}" && "${MODE:-}" != "--apply" ]]; then
  echo "Unknown argument: ${MODE}. Only '--apply' is supported." >&2
  exit 3
fi

# --- Preconditions -----------------------------------------------------------
require() {
  command -v "$1" >/dev/null 2>&1 || { echo "Missing required tool: $1" >&2; exit 2; }
}

require gh
if ! gh auth status >/dev/null 2>&1; then
  echo "You are not authenticated with gh. Run: gh auth login" >&2
  exit 2
fi

# Verify repo exists / access
if ! gh repo view "$REPO" >/dev/null 2>&1; then
  echo "Repo not accessible: $REPO" >&2
  exit 2
fi

# --- Helpers -----------------------------------------------------------------
JSON_ESC() {
  # minimal JSON escaper for strings
  python3 - <<'PY' "$1"
import json,sys
print(json.dumps(sys.argv[1]))
PY
}

upsert_label() {
  local name="$1" color="$2" desc="$3"
  local name_json; name_json="$(JSON_ESC "$name")"
  local desc_json; desc_json="$(JSON_ESC "$desc")"

  if gh label list --repo "$REPO" --limit 500 --json name | jq -e --arg n "$name" '.[] | select(.name==$n)' >/dev/null; then
    echo "⊙ label exists: $name -> updating (color=$color)"
    if $APPLY; then
      gh api \
        --method PATCH \
        -H "Accept: application/vnd.github+json" \
        "/repos/${REPO}/labels/$(printf '%s' "$name" | sed 's/ /%20/g')" \
        -f "new_name=$name" \
        -f "color=${color#\#}" \
        -f "description=$desc" >/dev/null
    fi
  else
    echo "+ create label: $name (color=$color)"
    if $APPLY; then
      gh api \
        --method POST \
        -H "Accept: application/vnd.github+json" \
        "/repos/${REPO}/labels" \
        -f "name=$name" \
        -f "color=${color#\#}" \
        -f "description=$desc" >/dev/null
    fi
  fi
}

upsert_milestone() {
  local title="$1" due_on="${2:-}" state="open"
  local title_json; title_json="$(JSON_ESC "$title")"

  # Lookup existing by title
  local existing_id
  existing_id="$(gh api -H "Accept: application/vnd.github+json" "/repos/${REPO}/milestones?state=all&per_page=100" | \
                jq -r --arg t "$title" '.[] | select(.title==$t) | .number' | head -n1 || true)"

  if [[ -n "$existing_id" && "$existing_id" != "null" ]]; then
    echo "⊙ milestone exists: $title -> updating"
    if $APPLY; then
      if [[ -n "$due_on" ]]; then
        gh api \
          --method PATCH \
          -H "Accept: application/vnd.github+json" \
          "/repos/${REPO}/milestones/${existing_id}" \
          -f "title=$title" \
          -f "state=$state" \
          -f "due_on=$due_on" >/dev/null
      else
        gh api \
          --method PATCH \
          -H "Accept: application/vnd.github+json" \
          "/repos/${REPO}/milestones/${existing_id}" \
          -f "title=$title" \
          -f "state=$state" >/dev/null
      fi
    fi
  else
    echo "+ create milestone: $title ${due_on:+(due $due_on)}"
    if $APPLY; then
      if [[ -n "$due_on" ]]; then
        gh api \
          --method POST \
          -H "Accept: application/vnd.github+json" \
          "/repos/${REPO}/milestones" \
          -f "title=$title" \
          -f "state=$state" \
          -f "due_on=$due_on" >/dev/null
      else
        gh api \
          --method POST \
          -H "Accept: application/vnd.github+json" \
          "/repos/${REPO}/milestones" \
          -f "title=$title" \
          -f "state=$state" >/dev/null
      fi
    fi
  fi
}

# --- Label Set ---------------------------------------------------------------
# Colors use GitHub-friendly hex (no leading '#')
# Choose high-contrast, consistent palette.
declare -a LABELS=(
  # priority
  "priority:P0|d73a4a|Highest priority (blockers for GA)"
  "priority:P1|fbca04|High priority (pre-GA must-have)"
  "priority:P2|0e8a16|Medium priority (post-GA)"

  # area
  "area:security|5319e7|Security, signing, keys, SBOM"
  "area:linux|1d76db|Linux packaging, distros, repos"
  "area:windows|0052cc|Windows packaging and CI"
  "area:macos|6f42c1|macOS/Homebrew packaging and CI"
  "area:packaging|bfd4f2|Packaging definitions and scripts"
  "area:ci|0366d6|CI/CD workflows, runners, infra"
  "area:docs|c5def5|Documentation tasks"
  "area:registry|0e8a16|External registries and caches"

  # type
  "type:feature|a2eeef|New feature"
  "type:improvement|c2e0c6|Enhancement/improvement"
  "type:bug|d73a4a|Defect/bug"

  # workflow / misc
  "epic|f9d0c4|Large multi-issue effort"
  "blocked|d4c5f9|Blocked by external/internal dependency"
  "good first issue|7057ff|Appropriate for first-time contributors"
  "needs triage|ededed|Awaiting triage"
)

echo "==> Labels"
for row in "${LABELS[@]}"; do
  IFS="|" read -r name color desc <<<"$row"
  upsert_label "$name" "$color" "$desc"
done

# --- Milestones --------------------------------------------------------------
SPRINT1="${SPRINT1:-Sprint 1 (P0)}"
SPRINT2="${SPRINT2:-Sprint 2 (P1)}"
SPRINT3="${SPRINT3:-Sprint 3 (P2)}"

# Accept dates in YYYY-MM-DD or full ISO; GitHub expects ISO 8601
# If not set, we create without due dates.
echo "==> Milestones"
upsert_milestone "$SPRINT1" "${SPRINT1_DUE:-}"
upsert_milestone "$SPRINT2" "${SPRINT2_DUE:-}"
upsert_milestone "$SPRINT3" "${SPRINT3_DUE:-}"

echo
if $APPLY; then
  echo "✓ Applied labels and milestones to $REPO"
else
  echo "ⓘ Dry-run complete. Re-run with '--apply' to make changes:"
  echo "   bash $0 $REPO --apply"
fi
