# The (future of the) Black code style

## Preview style

(labels/preview-style)=

Experimental, potentially disruptive style changes are gathered under the `--preview`
CLI flag. At the end of each year, these changes may be adopted into the default style,
as described in [The Black Code Style](index.md). Because the functionality is
experimental, feedback and issue reports are highly encouraged!

(labels/preview-features)=

Currently, the following features are included in the preview style:

- `wrap_comprehension_in`: Wrap the `in` clause of list and dictionary comprehensions
  across lines if it would otherwise exceed the maximum line length.
  ([see below](labels/wrap-comprehension-in))
- `simplify_power_operator_hugging`: Use a simpler implementation of the power operator
  "hugging" logic (removing whitespace around `**` in simple expressions), which applies
  also in the rare case the exponentiation is split into separate lines.
  ([see below](labels/simplify-power-operator))
- `wrap_long_dict_values_in_parens`: Add parentheses around long values in dictionaries.
  ([see below](labels/wrap-long-dict-values))
- `fix_if_guard_explosion_in_case_statement`: fixed exploding of the if guard in case
  patterns which have trailing commas in them, even if the guard expression fits in one
  line

(labels/wrap-comprehension-in)=

### Wrapping long comprehension `in` clauses

When a list or dictionary comprehension has a long `in` clause that would exceed the
maximum line length, Black will wrap it across multiple lines for better readability.
This helps keep comprehensions readable when the iterable expression is complex or
lengthy.

For example:

```python
# Before
result = [
    very_very_very_very_very_long_item
    for very_very_very_very_very_long_item in some_very_very_very_very_very_very_long_function_name
]
```

will be formatted to:

```python
# After
result = [
    very_very_very_very_very_long_item
    for very_very_very_very_very_long_item in (
        some_very_very_very_very_very_very_long_function_name
    )
]
```

This also applies to dictionary comprehensions:

```python
# Before
mapping = {
    very_long_key: very_very_very_long_item
    for very_long_key, very_very_very_long_item in very_very_very_very_long_function_name
}
```

will be formatted to:

```python
# After
mapping = {
    very_long_key: very_very_very_long_item
    for very_long_key, very_very_very_long_item in (
        very_very_very_very_long_function_name
    )
}
```

(labels/simplify-power-operator)=

### Simplified power operator whitespace handling

Black's power operator "hugging" logic removes whitespace around `**` in simple
expressions (e.g., `x**2` instead of `x ** 2`). This feature uses a simpler, more
consistent implementation that also applies when exponentiation is split across lines.

For example:

```python
# Simple expressions - whitespace is removed
result = x**2 + y**3
value = base**exponent
```

When the exponentiation is split across lines (rare), the simplified logic ensures
consistent formatting:

```python
# Complex expression split across lines
result = (
    some_very_long_base_expression
    **some_very_long_exponent_expression
    **some_very_long_third_expression
)
```

This feature primarily improves the internal consistency of Black's formatting logic
rather than making dramatic visual changes to most code.

(labels/wrap-long-dict-values)=

### Improved parentheses management in dicts

For dict literals with long values, they are now wrapped in parentheses. Unnecessary
parentheses are now removed. For example:

```python
my_dict = {
    "a key in my dict": a_very_long_variable
    * and_a_very_long_function_call()
    / 100000.0,
    "another key": (short_value),
}
```

will be changed to:

```python
my_dict = {
    "a key in my dict": (
        a_very_long_variable * and_a_very_long_function_call() / 100000.0
    ),
    "another key": short_value,
}
```

## Unstable style

(labels/unstable-style)=

In the past, the preview style included some features with known bugs, so that we were
unable to move these features to the stable style. Therefore, such features are now
moved to the `--unstable` style. All features in the `--preview` style are expected to
make it to next year's stable style; features in the `--unstable` style will be
stabilized only if issues with them are fixed. If bugs are discovered in a `--preview`
feature, it is demoted to the `--unstable` style. To avoid thrash when a feature is
demoted from the `--preview` to the `--unstable` style, users can use the
`--enable-unstable-feature` flag to enable specific unstable features.

(labels/unstable-features)=

The unstable style additionally includes the following features:

- `hug_parens_with_braces_and_square_brackets`: More compact formatting of nested
  brackets. ([see below](labels/hug-parens))
- `string_processing`: Split long string literals and related changes.
  ([see below](labels/string-processing))

(labels/hug-parens)=

### Improved multiline dictionary and list indentation for sole function parameter

For better readability and less verticality, _Black_ now pairs parentheses ("(", ")")
with braces ("{", "}") and square brackets ("[", "]") on the same line. For example:

```python
foo(
    [
        1,
        2,
        3,
    ]
)

nested_array = [
    [
        1,
        2,
        3,
    ]
]
```

will be changed to:

```python
foo([
    1,
    2,
    3,
])

nested_array = [[
    1,
    2,
    3,
]]
```

This also applies to list and dictionary unpacking:

```python
foo(
    *[
        a_long_function_name(a_long_variable_name)
        for a_long_variable_name in some_generator
    ]
)
```

will become:

```python
foo(*[
    a_long_function_name(a_long_variable_name)
    for a_long_variable_name in some_generator
])
```

You can use a magic trailing comma to avoid this compacting behavior; by default,
_Black_ will not reformat the following code:

```python
foo(
    [
        1,
        2,
        3,
    ],
)
```

(labels/string-processing)=

### Improved string processing

_Black_ will split long string literals and merge short ones. Parentheses are used where
appropriate. When split, parts of f-strings that don't need formatting are converted to
plain strings. f-strings will not be merged if they contain internal quotes and it would
change their quotation mark style. Line continuation backslashes are converted into
parenthesized strings. Unnecessary parentheses are stripped. The stability and status of
this feature is tracked in [this issue](https://github.com/psf/black/issues/2188).
