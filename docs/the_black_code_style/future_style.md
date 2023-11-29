# The (future of the) Black code style

```{warning}
Changes to this document often aren't tied and don't relate to releases of
_Black_. It's recommended that you read the latest version available.
```

## Using backslashes for with statements

[Backslashes are bad and should be never be used](labels/why-no-backslashes) however
there is one exception: `with` statements using multiple context managers. Before Python
3.9 Python's grammar does not allow organizing parentheses around the series of context
managers.

We don't want formatting like:

```py3
with make_context_manager1() as cm1, make_context_manager2() as cm2, make_context_manager3() as cm3, make_context_manager4() as cm4:
    ...  # nothing to split on - line too long
```

So _Black_ will, when we implement this, format it like this:

```py3
with \
     make_context_manager1() as cm1, \
     make_context_manager2() as cm2, \
     make_context_manager3() as cm3, \
     make_context_manager4() as cm4 \
:
    ...  # backslashes and an ugly stranded colon
```

Although when the target version is Python 3.9 or higher, _Black_ uses parentheses
instead in `--preview` mode (see below) since they're allowed in Python 3.9 and higher.

An alternative to consider if the backslashes in the above formatting are undesirable is
to use {external:py:obj}`contextlib.ExitStack` to combine context managers in the
following way:

```python
with contextlib.ExitStack() as exit_stack:
    cm1 = exit_stack.enter_context(make_context_manager1())
    cm2 = exit_stack.enter_context(make_context_manager2())
    cm3 = exit_stack.enter_context(make_context_manager3())
    cm4 = exit_stack.enter_context(make_context_manager4())
    ...
```

(labels/preview-style)=

## Preview style

Experimental, potentially disruptive style changes are gathered under the `--preview`
CLI flag. At the end of each year, these changes may be adopted into the default style,
as described in [The Black Code Style](index.md). Because the functionality is
experimental, feedback and issue reports are highly encouraged!

### Improved string processing

_Black_ will split long string literals and merge short ones. Parentheses are used where
appropriate. When split, parts of f-strings that don't need formatting are converted to
plain strings. User-made splits are respected when they do not exceed the line length
limit. Line continuation backslashes are converted into parenthesized strings.
Unnecessary parentheses are stripped. The stability and status of this feature is
tracked in [this issue](https://github.com/psf/black/issues/2188).

### Improved line breaks

For assignment expressions, _Black_ now prefers to split and wrap the right side of the
assignment instead of left side. For example:

```python
some_dict[
    "with_a_long_key"
] = some_looooooooong_module.some_looooooooooooooong_function_name(
    first_argument, second_argument, third_argument
)
```

will be changed to:

```python
some_dict["with_a_long_key"] = (
    some_looooooooong_module.some_looooooooooooooong_function_name(
        first_argument, second_argument, third_argument
    )
)
```

### Improved parentheses management

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

=======

### Form feed characters

_Black_ will now retain form feed characters on otherwise empty lines at the module
level. Only one form feed is retained for a group of consecutive empty lines. Where
there are two empty lines in a row, the form feed will be placed on the second line.

_Black_ already retained form feed literals inside a comment or inside a string. This
remains the case.
