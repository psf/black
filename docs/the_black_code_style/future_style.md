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

So _Black_ will eventually format it like this:

```py3
with \
     make_context_manager1() as cm1, \
     make_context_manager2() as cm2, \
     make_context_manager3() as cm3, \
     make_context_manager4() as cm4 \
:
    ...  # backslashes and an ugly stranded colon
```

Although when the target version is Python 3.9 or higher, _Black_ will use parentheses
instead since they're allowed in Python 3.9 and higher.

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
as described in [The Black Code Style](./index.rst). Because the functionality is
experimental, feedback and issue reports are highly encouraged!

### Improved string processing

_Black_ will split long string literals and merge short ones. Parentheses are used where
appropriate. When split, parts of f-strings that don't need formatting are converted to
plain strings. User-made splits are respected when they do not exceed the line length
limit. Line continuation backslashes are converted into parenthesized strings.
Unnecessary parentheses are stripped. The stability and status of this feature is
tracked in [this issue](https://github.com/psf/black/issues/2188).

### Removing newlines in the beginning of code blocks

_Black_ will remove newlines in the beginning of new code blocks, i.e. when the
indentation level is increased. For example:

```python
def my_func():

    print("The line above me will be deleted!")
```

will be changed to:

```python
def my_func():
    print("The line above me will be deleted!")
```

This new feature will be applied to **all code blocks**: `def`, `class`, `if`, `for`,
`while`, `with`, `case` and `match`.

### Improved parentheses management

_Black_ will format parentheses around return annotations similarly to other sets of
parentheses. For example:

```python
def foo() -> (int):
    ...

def foo() -> looooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong:
    ...
```

will be changed to:

```python
def foo() -> int:
    ...


def foo() -> (
    looooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong
):
    ...
```

And, extra parentheses in `await` expressions and `with` statements are removed. For
example:

```python
with ((open("bla.txt")) as f, open("x")):
    ...

async def main():
    await (asyncio.sleep(1))
```

will be changed to:

```python
with open("bla.txt") as f, open("x"):
    ...


async def main():
    await asyncio.sleep(1)
```

### Enforced newline after module docstrings

A single blank line after module docstrings will be enforced, this applies to single and
multi-line docstrings.

```python
"""Utility functions and constants."""
import functools
```

```python
"""
Utility functions and constants.
"""


import functools
```

will be changed to:

```python
"""Utility functions and constants."""

import functools
```

```python
"""
Utility functions and constants.
"""

import functools
```
