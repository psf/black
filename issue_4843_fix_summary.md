# Fix for Issue #4843: Black 25.11.0 Removing %% [markdown] Comments

## Problem Description

In Black version 25.11.0, the formatter was incorrectly removing `%% [markdown]`
comments from Python files that use Jupytext's percent format. This worked correctly in
version 25.9.0 but was broken in 25.11.0.

The issue occurs when processing `.py` files that contain Jupytext cell type indicators
like:

```python
%% [markdown]
fmt: off
fmt: on
```

Black was treating these as invalid IPython cell magics and removing them, when they
should be preserved as they indicate cell types in Jupytext's percent format.

## Root Cause

The issue was in the `validate_cell` function in `src/black/handle_ipynb_magics.py`.
This function checks if a cell contains valid IPython magics, and if not, it raises
`NothingChanged` to skip processing the cell.

The function was rejecting `%% [markdown]` because:

1. It starts with `%%` (like IPython cell magics)
2. `[markdown]` is not in the list of recognized Python cell magics
3. The function didn't distinguish between actual IPython magics and Jupytext cell type
   indicators

## Solution

The fix adds a specific check in the `validate_cell` function to recognize Jupytext cell
type indicators (lines that start with `%% [` and end with `]`) and accept them without
raising `NothingChanged`.

### Code Changes

In `src/black/handle_ipynb_magics.py`, the `validate_cell` function was modified to add
this check:

```python
# Check if this is a Jupytext cell type indicator (e.g., %% [markdown])
# These should be preserved as they're not actual IPython magics
if line.startswith("%% [") and line.endswith("]"):
    return
```

This check is placed before the existing validation logic, so Jupytext indicators are
accepted without further processing.

## Testing

A new test case was added to `tests/test_ipynb.py`:

```python
def test_jupytext_markdown_cell_type_indicator() -> None:
    """Test that Jupytext markdown cell type indicators are preserved.

    Jupytext uses `%% [cell_type]` syntax to indicate cell types in percent format.
    These should not be treated as IPython magics and should be preserved.
    See issue #4843.
    """
    src = "%% [markdown]\nfmt: off\nfmt: on"
    # This should not raise NothingChanged, but should process normally
    result = format_cell(src, fast=True, mode=JUPYTER_MODE)
    # The cell type indicator should be preserved
    assert "%% [markdown]" in result
```

## Verification

Comprehensive tests were run to ensure:

1. Jupytext cell type indicators are preserved: `%% [markdown]`, `%% [code]`, `%% [raw]`
2. Valid IPython cell magics continue to work: `%%time`, `%%python`, `%%capture`
3. Invalid IPython cell magics are still rejected: `%%invalid_magic`, `%%bash`
4. Edge cases are handled correctly

All tests pass, confirming the fix works correctly without breaking existing
functionality.
