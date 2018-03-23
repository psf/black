# Technical Overview

## The philosophy behind *Black*

*Black* reformats entire files in place.  It is not configurable.  It
doesn't take previous formatting into account.  It doesn't reformat
blocks that start with `# fmt: off` and end with `# fmt: on`.  It also
recognizes [YAPF](https://github.com/google/yapf)'s block comments to
the same effect, as a courtesy for straddling code.

## How *Black* formats files

*Black* ignores previous formatting and applies uniform horizontal
and vertical whitespace to your code.  The rules for horizontal
whitespace are pretty obvious and can be summarized as: do whatever
makes `pycodestyle` happy.

As for vertical whitespace, *Black* tries to render one full expression
or simple statement per line.  If this fits the allotted line length,
great.

```py3
# in:

l = [1,
     2,
     3,
]

# out:

l = [1, 2, 3]
```

If not, *Black* will look at the contents of the first outer matching
brackets and put that in a separate indented line.

```py3
# in:

l = [[n for n in list_bosses()], [n for n in list_employees()]]

# out:

l = [
    [n for n in list_bosses()], [n for n in list_employees()]
]
```

If that still doesn't fit the bill, it will decompose the internal
expression further using the same rule, indenting matching brackets
every time.  If the contents of the matching brackets pair are
comma-separated (like an argument list, or a dict literal, and so on)
then *Black* will first try to keep them on the same line with the
matching brackets.  If that doesn't work, it will put all of them in
separate lines.

```py3
# in:

def very_important_function(template: str, *variables, file: os.PathLike, debug: bool = False):
    """Applies `variables` to the `template` and writes to `file`."""
    with open(file, 'w') as f:
        ...

# out:

def very_important_function(
    template: str,
    *variables,
    file: os.PathLike,
    debug: bool = False,
):
    """Applies `variables` to the `template` and writes to `file`."""
    with open(file, 'w') as f:
        ...
```

You might have noticed that closing brackets are always dedented and
that a trailing comma is always added.  Such formatting produces smaller
diffs; when you add or remove an element, it's always just one line.
Also, having the closing bracket dedented provides a clear delimiter
between two distinct sections of the code that otherwise share the same
indentation level (like the arguments list and the docstring in the
example above).

Unnecessary trailing commas are removed if an expression fits in one
line.  This makes it 1% more likely that your line won't exceed the
allotted line length limit.

*Black* avoids spurious vertical whitespace.  This is in the spirit of
PEP 8 which says that in-function vertical whitespace should only be
used sparingly.  One exception is control flow statements: *Black* will
always emit an extra empty line after ``return``, ``raise``, ``break``,
``continue``, and ``yield``.  This is to make changes in control flow
more prominent to readers of your code.

That's it.  The rest of the whitespace formatting rules follow PEP 8 and
are designed to keep `pycodestyle` quiet.

## Line length

You probably noticed the peculiar default line length.  *Black* defaults
to 88 characters per line, which happens to be 10% over 80.  This number
was found to produce significantly shorter files than sticking with 80
(the most popular), or even 79 (used by the standard library).  In
general, [90-ish seems like the wise choice](https://youtu.be/wf-BqAjZb8M?t=260).

If you're paid by the line of code you write, you can pass
`--line-length` with a lower number.  *Black* will try to respect that.
However, sometimes it won't be able to without breaking other rules.  In
those rare cases, auto-formatted code will exceed your allotted limit.

You can also increase it, but remember that people with sight disabilities
find it harder to work with line lengths exceeding 100 characters.
It also adversely affects side-by-side diff review  on typical screen
resolutions.  Long lines also make it harder to present code neatly
in documentation or talk slides.

If you're using Flake8, you can bump `max-line-length` to 88 and forget
about it.  Alternatively, use [Bugbear](https://github.com/PyCQA/flake8-bugbear)'s
B950 warning instead of E501 and keep the max line length at 80 which
you are probably already using.  You'd do it like this:

```ini
[flake8]
max-line-length = 80
...
select = C,E,F,W,B,B950
ignore = E501
```

You'll find *Black*'s own .flake8 config file is configured like this.
If you're curious about the reasoning behind B950, Bugbear's documentation
explains it.  The tl;dr is "it's like highway speed limits, we won't
bother you if you overdo it by a few km/h".

## Empty lines

*Black* will allow single empty lines left by the original editors,
except when they're added within parenthesized expressions.  Since such
expressions are always reformatted to fit minimal space, this whitespace
is lost.

It will also insert proper spacing before and after function definitions.
It's one line before and after inner functions and two lines before and
after module-level functions.  *Black* will put those empty lines also
between the function definition and any standalone comments that
immediately precede the given function.  If you want to comment on the
entire function, use a docstring or put a leading comment in the function
body.

## Editor integration

* Visual Studio Code: [joslarson.black-vscode](https://marketplace.visualstudio.com/items?itemName=joslarson.black-vscode)

Any tool that can pipe code through *Black* using its stdio mode (just
[use `-` as the file name](http://www.tldp.org/LDP/abs/html/special-chars.html#DASHREF2)).
The formatted code will be returned on stdout (unless `--check` was
passed).  *Black* will still emit messages on stderr but that shouldn't
affect your use case.

There is currently no integration with any other text editors. Vim and
Atom/Nuclide integration is planned by the author, others will require
external contributions.

Patches welcome! ✨ 🍰 ✨
