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
     make_context_manager(1) as cm1, \
     make_context_manager(2) as cm2, \
     make_context_manager(3) as cm3, \
     make_context_manager(4) as cm4 \
:
    ...  # backslashes and an ugly stranded colon
```

Although when the target version is Python 3.9 or higher, _Black_ will use parentheses
instead since they're allowed in Python 3.9 and higher.

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
