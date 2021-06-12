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

## Improved string processing

Currently, _Black_ does not split long strings to fit the line length limit. Currently,
there is [an experimental option](labels/experimental-string) to enable splitting
strings. We plan to enable this option by default once it is fully stable. This is
tracked in [this issue](https://github.com/psf/black/issues/2188).
