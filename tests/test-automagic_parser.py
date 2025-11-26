import ast
import re

"""
    AUTHOR: ARRIS MANDUMA@2025-11-25
"""
def is_ipython_magic(cell_source):
    """
    Determines whether a cell contains an IPython line or cell magic.
    """
    lines = cell_source.strip().splitlines()
    if not lines:
        return False

    first = lines[0].strip()
    return (
        first.startswith("%%") or  # cell magic
        first.startswith("%") or   # line magic
        first.startswith("!")      # shell escape
    )

def check_cell_syntax(cell_source):
    """
    Attempt to validate syntax of a cell.
    - Returns valid Python if ast.parse succeeds.
    - If SyntaxError occurs, checks if it might be IPython magic.
    """
    stripped = cell_source.strip()

    if not stripped:
        return "Skipped (Empty cell)"

    try:
        ast.parse(cell_source)
        return "Valid Python"

    except SyntaxError:
        if is_ipython_magic(cell_source):
            return "Skipped (IPython magic)"
        return "Syntax Error (Invalid Python)"

    except ValueError as e:
        return f"ValueError: {e}"


notebook_content = """
# This is a valid Python cell
x = 10
print(x)

%timeit x = 10  # IPython line magic

if x == 10:  # Valid Python with a syntax error
print("x is 10") # Missing indentation

%%writefile script.py
print("This is a script") # IPython cell magic
"""

cells = re.split(r'\n\s*\n', notebook_content.strip())

print("\n--- Syntax Check Results ---")
for i, cell in enumerate(cells, start=1):
    result = check_cell_syntax(cell)
    print(f"\nCell {i}: {result}")
    if "Syntax Error" in result:
        print("  Code snippet:", repr(cell.strip()[:80]))
