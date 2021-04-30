# The (future of the) Black Code Style

<div class="admonition warning">
    <p class="admonition-title">Warning</p>
    <p>
      Changes to this document often aren't tied and don't relate to releases of <em>
      Black</em>. It's recommended that you read the latest version available.
    </p>
</div>

## Using backslashes for with statements

[Backslashes are bad and should be never be used](labels/why-no-backslashes)) however
there is one exception: `with` statements using multiple context managers. Python's
grammar does not allow organizing parentheses around the series of context managers.

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
