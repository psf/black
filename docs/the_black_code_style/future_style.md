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
