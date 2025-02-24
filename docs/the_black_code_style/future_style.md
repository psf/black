# The (future of the) Black code style

## Preview style

(labels/preview-style)=

Experimental, potentially disruptive style changes are gathered under the `--preview`
CLI flag. At the end of each year, these changes may be adopted into the default style,
as described in [The Black Code Style](index.md). Because the functionality is
experimental, feedback and issue reports are highly encouraged!

In the past, the preview style included some features with known bugs, so that we were
unable to move these features to the stable style. Therefore, such features are now
moved to the `--unstable` style. All features in the `--preview` style are expected to
make it to next year's stable style; features in the `--unstable` style will be
stabilized only if issues with them are fixed. If bugs are discovered in a `--preview`
feature, it is demoted to the `--unstable` style. To avoid thrash when a feature is
demoted from the `--preview` to the `--unstable` style, users can use the
`--enable-unstable-feature` flag to enable specific unstable features.

(labels/preview-features)=

Currently, the following features are included in the preview style:

- `always_one_newline_after_import`: Always force one blank line after import
  statements, except when the line after the import is a comment or an import statement
- `wrap_long_dict_values_in_parens`: Add parentheses around long values in dictionaries
  ([see below](labels/wrap-long-dict-values))
- `fix_fmt_skip_in_one_liners`: Fix `# fmt: skip` behaviour on one-liner declarations,
  such as `def foo(): return "mock"  # fmt: skip`, where previously the declaration
  would have been incorrectly collapsed.

(labels/unstable-features)=

The unstable style additionally includes the following features:

- `string_processing`: split long string literals and related changes
  ([see below](labels/string-processing))
- `multiline_string_handling`: more compact formatting of expressions involving
  multiline strings ([see below](labels/multiline-string-handling))
- `hug_parens_with_braces_and_square_brackets`: more compact formatting of nested
  brackets ([see below](labels/hug-parens))

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
change their quotation mark style. User-made splits are respected when they do not
exceed the line length limit. Line continuation backslashes are converted into
parenthesized strings. Unnecessary parentheses are stripped. The stability and status of
this feature istracked in [this issue](https://github.com/psf/black/issues/2188).

(labels/multiline-string-handling)=

### Improved multiline string handling

_Black_ is smarter when formatting multiline strings, especially in function arguments,
to avoid introducing extra line breaks. Previously, it would always consider multiline
strings as not fitting on a single line. With this new feature, _Black_ looks at the
context around the multiline string to decide if it should be inlined or split to a
separate line. For example, when a multiline string is passed to a function, _Black_
will only split the multiline string if a line is too long or if multiple arguments are
being passed.

For example, _Black_ will reformat

```python
textwrap.dedent(
    """\
    This is a
    multiline string
"""
)
```

to:

```python
textwrap.dedent("""\
    This is a
    multiline string
""")
```

And:

```python
MULTILINE = """
foobar
""".replace(
    "\n", ""
)
```

to:

```python
MULTILINE = """
foobar
""".replace("\n", "")
```

Implicit multiline strings are special, because they can have inline comments. Strings
without comments are merged, for example

```python
s = (
    "An "
    "implicit "
    "multiline "
    "string"
)
```

becomes

```python
s = "An implicit multiline string"
```

A comment on any line of the string (or between two string lines) will block the
merging, so

```python
s = (
    "An "  # Important comment concerning just this line
    "implicit "
    "multiline "
    "string"
)
```

and

```python
s = (
    "An "
    "implicit "
    # Comment in between
    "multiline "
    "string"
)
```

will not be merged. Having the comment after or before the string lines (but still
inside the parens) will merge the string. For example

```python
s = (  # Top comment
    "An "
    "implicit "
    "multiline "
    "string"
    # Bottom comment
)
```

becomes

```python
s = (  # Top comment
    "An implicit multiline string"
    # Bottom comment
)
```
