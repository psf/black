# Symmetric formatting for multi-line list concatenations

Black formats list concatenations that must be split across multiple lines in a
symmetric, parenthesized style to improve readability.

When an assignment’s right-hand side is a concatenation of two list displays or list
comprehensions and the entire statement would exceed the configured line length, Black
will wrap the right-hand side in parentheses and place the `+` operator at the start of
the following line.

## Example

Before (too long to fit on one line):

```python
search_fields = ["file__%s" % field for field in FileAdmin.search_fields] + [
    "resource__%s" % field for field in ResourceAdmin.search_fields
]
```

After:

```python
search_fields = (
    ["file__%s" % field for field in FileAdmin.search_fields]
    + ["resource__%s" % field for field in ResourceAdmin.search_fields]
)
```

## Scope and rules

- Applies when:
  - The statement is an assignment (`=`).
  - The right-hand side is a binary `+` expression where both operands are list displays
    (e.g., `[1, 2]`) or list comprehensions.
  - The whole line would otherwise exceed the configured line length.
- The entire right-hand side is wrapped in parentheses, with:
  - The first list on its own line.
  - The `+` operator starting the next line.
  - The second list following the `+` on the same line.

## Non-goals

- Does not change formatting when either operand is not a list (e.g., a variable,
  function call result, or other non-list expression).
- Does not reformat already parenthesized and symmetric concatenations.
- Does not special-case chained concatenations (e.g., `a + b + c`).
