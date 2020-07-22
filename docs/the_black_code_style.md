# The _Black_ code style

## Code style

_Black_ reformats entire files in place. It is not configurable. It doesn't take
previous formatting into account. It doesn't reformat blocks that start with
`# fmt: off` and end with `# fmt: on`. `# fmt: on/off` have to be on the same level of
indentation. It also recognizes [YAPF](https://github.com/google/yapf)'s block comments
to the same effect, as a courtesy for straddling code.

### How _Black_ wraps lines

_Black_ ignores previous formatting and applies uniform horizontal and vertical
whitespace to your code. The rules for horizontal whitespace can be summarized as: do
whatever makes `pycodestyle` happy. The coding style used by _Black_ can be viewed as a
strict subset of PEP 8.

As for vertical whitespace, _Black_ tries to render one full expression or simple
statement per line. If this fits the allotted line length, great.

```py3
# in:

j = [1,
     2,
     3
]

# out:

j = [1, 2, 3]
```

If not, _Black_ will look at the contents of the first outer matching brackets and put
that in a separate indented line.

```py3
# in:

ImportantClass.important_method(exc, limit, lookup_lines, capture_locals, extra_argument)

# out:

ImportantClass.important_method(
    exc, limit, lookup_lines, capture_locals, extra_argument
)
```

If that still doesn't fit the bill, it will decompose the internal expression further
using the same rule, indenting matching brackets every time. If the contents of the
matching brackets pair are comma-separated (like an argument list, or a dict literal,
and so on) then _Black_ will first try to keep them on the same line with the matching
brackets. If that doesn't work, it will put all of them in separate lines.

```py3
# in:

def very_important_function(template: str, *variables, file: os.PathLike, engine: str, header: bool = True, debug: bool = False):
    """Applies `variables` to the `template` and writes to `file`."""
    with open(file, 'w') as f:
        ...

# out:

def very_important_function(
    template: str,
    *variables,
    file: os.PathLike,
    engine: str,
    header: bool = True,
    debug: bool = False,
):
    """Applies `variables` to the `template` and writes to `file`."""
    with open(file, "w") as f:
        ...
```

_Black_ prefers parentheses over backslashes, and will remove backslashes if found.

```py3
# in:

if some_short_rule1 \
  and some_short_rule2:
      ...

# out:

if some_short_rule1 and some_short_rule2:
  ...


# in:

if some_long_rule1 \
  and some_long_rule2:
    ...

# out:

if (
    some_long_rule1
    and some_long_rule2
):
    ...

```

Backslashes and multiline strings are one of the two places in the Python grammar that
break significant indentation. You never need backslashes, they are used to force the
grammar to accept breaks that would otherwise be parse errors. That makes them confusing
to look at and brittle to modify. This is why _Black_ always gets rid of them.

If you're reaching for backslashes, that's a clear signal that you can do better if you
slightly refactor your code. I hope some of the examples above show you that there are
many ways in which you can do it.

However there is one exception: `with` statements using multiple context managers.
Python's grammar does not allow organizing parentheses around the series of context
managers.

We don't want formatting like:

```py3
with make_context_manager1() as cm1, make_context_manager2() as cm2, make_context_manager3() as cm3, make_context_manager4() as cm4:
    ...  # nothing to split on - line too long
```

So _Black_ will now format it like this:

```py3
with \
     make_context_manager(1) as cm1, \
     make_context_manager(2) as cm2, \
     make_context_manager(3) as cm3, \
     make_context_manager(4) as cm4 \
:
    ...  # backslashes and an ugly stranded colon
```

You might have noticed that closing brackets are always dedented and that a trailing
comma is always added. Such formatting produces smaller diffs; when you add or remove an
element, it's always just one line. Also, having the closing bracket dedented provides a
clear delimiter between two distinct sections of the code that otherwise share the same
indentation level (like the arguments list and the docstring in the example above).

If a data structure literal (tuple, list, set, dict) or a line of "from" imports cannot
fit in the allotted length, it's always split into one element per line. This minimizes
diffs as well as enables readers of code to find which commit introduced a particular
entry. This also makes _Black_ compatible with [isort](https://pypi.org/p/isort/) with
the following configuration.

<details>
<summary>A compatible `.isort.cfg`</summary>

```cfg
[settings]
multi_line_output = 3
include_trailing_comma = True
force_grid_wrap = 0
use_parentheses = True
ensure_newline_before_comments = True
line_length = 88
```

The equivalent command line is:

```
$ isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --use-parentheses --line-width=88 [ file.py ]
```

</details>

### Line length

You probably noticed the peculiar default line length. _Black_ defaults to 88 characters
per line, which happens to be 10% over 80. This number was found to produce
significantly shorter files than sticking with 80 (the most popular), or even 79 (used
by the standard library). In general,
[90-ish seems like the wise choice](https://youtu.be/wf-BqAjZb8M?t=260).

If you're paid by the line of code you write, you can pass `--line-length` with a lower
number. _Black_ will try to respect that. However, sometimes it won't be able to without
breaking other rules. In those rare cases, auto-formatted code will exceed your allotted
limit.

You can also increase it, but remember that people with sight disabilities find it
harder to work with line lengths exceeding 100 characters. It also adversely affects
side-by-side diff review on typical screen resolutions. Long lines also make it harder
to present code neatly in documentation or talk slides.

If you're using Flake8, you can bump `max-line-length` to 88 and forget about it.
Alternatively, use [Bugbear](https://github.com/PyCQA/flake8-bugbear)'s B950 warning
instead of E501 and keep the max line length at 80 which you are probably already using.
You'd do it like this:

```ini
[flake8]
max-line-length = 80
...
select = C,E,F,W,B,B950
ignore = E203, E501, W503
```

You'll find _Black_'s own .flake8 config file is configured like this. Explanation of
why W503 and E203 are disabled can be found further in this documentation. And if you're
curious about the reasoning behind B950,
[Bugbear's documentation](https://github.com/PyCQA/flake8-bugbear#opinionated-warnings)
explains it. The tl;dr is "it's like highway speed limits, we won't bother you if you
overdo it by a few km/h".

**If you're looking for a minimal, black-compatible flake8 configuration:**

```ini
[flake8]
max-line-length = 88
extend-ignore = E203
```

### Empty lines

_Black_ avoids spurious vertical whitespace. This is in the spirit of PEP 8 which says
that in-function vertical whitespace should only be used sparingly.

_Black_ will allow single empty lines inside functions, and single and double empty
lines on module level left by the original editors, except when they're within
parenthesized expressions. Since such expressions are always reformatted to fit minimal
space, this whitespace is lost.

It will also insert proper spacing before and after function definitions. It's one line
before and after inner functions and two lines before and after module-level functions
and classes. _Black_ will not put empty lines between function/class definitions and
standalone comments that immediately precede the given function/class.

_Black_ will enforce single empty lines between a class-level docstring and the first
following field or method. This conforms to
[PEP 257](https://www.python.org/dev/peps/pep-0257/#multi-line-docstrings).

_Black_ won't insert empty lines after function docstrings unless that empty line is
required due to an inner function starting immediately after.

### Trailing commas

_Black_ will add trailing commas to expressions that are split by comma where each
element is on its own line. This includes function signatures.

Unnecessary trailing commas are removed if an expression fits in one line. This makes it
1% more likely that your line won't exceed the allotted line length limit. Moreover, in
this scenario, if you added another argument to your call, you'd probably fit it in the
same line anyway. That doesn't make diffs any larger.

One exception to removing trailing commas is tuple expressions with just one element. In
this case _Black_ won't touch the single trailing comma as this would unexpectedly
change the underlying data type. Note that this is also the case when commas are used
while indexing. This is a tuple in disguise: `numpy_array[3, ]`.

One exception to adding trailing commas is function signatures containing `*`, `*args`,
or `**kwargs`. In this case a trailing comma is only safe to use on Python 3.6. _Black_
will detect if your file is already 3.6+ only and use trailing commas in this situation.
If you wonder how it knows, it looks for f-strings and existing use of trailing commas
in function signatures that have stars in them. In other words, if you'd like a trailing
comma in this situation and _Black_ didn't recognize it was safe to do so, put it there
manually and _Black_ will keep it.

### Strings

_Black_ prefers double quotes (`"` and `"""`) over single quotes (`'` and `'''`). It
will replace the latter with the former as long as it does not result in more backslash
escapes than before.

_Black_ also standardizes string prefixes, making them always lowercase. On top of that,
if your code is already Python 3.6+ only or it's using the `unicode_literals` future
import, _Black_ will remove `u` from the string prefix as it is meaningless in those
scenarios.

The main reason to standardize on a single form of quotes is aesthetics. Having one kind
of quotes everywhere reduces reader distraction. It will also enable a future version of
_Black_ to merge consecutive string literals that ended up on the same line (see
[#26](https://github.com/psf/black/issues/26) for details).

Why settle on double quotes? They anticipate apostrophes in English text. They match the
docstring standard described in
[PEP 257](https://www.python.org/dev/peps/pep-0257/#what-is-a-docstring). An empty
string in double quotes (`""`) is impossible to confuse with a one double-quote
regardless of fonts and syntax highlighting used. On top of this, double quotes for
strings are consistent with C which Python interacts a lot with.

On certain keyboard layouts like US English, typing single quotes is a bit easier than
double quotes. The latter requires use of the Shift key. My recommendation here is to
keep using whatever is faster to type and let _Black_ handle the transformation.

If you are adopting _Black_ in a large project with pre-existing string conventions
(like the popular
["single quotes for data, double quotes for human-readable strings"](https://stackoverflow.com/a/56190)),
you can pass `--skip-string-normalization` on the command line. This is meant as an
adoption helper, avoid using this for new projects.

### Numeric literals

_Black_ standardizes most numeric literals to use lowercase letters for the syntactic
parts and uppercase letters for the digits themselves: `0xAB` instead of `0XAB` and
`1e10` instead of `1E10`. Python 2 long literals are styled as `2L` instead of `2l` to
avoid confusion between `l` and `1`.

### Line breaks & binary operators

_Black_ will break a line before a binary operator when splitting a block of code over
multiple lines. This is so that _Black_ is compliant with the recent changes in the
[PEP 8](https://www.python.org/dev/peps/pep-0008/#should-a-line-break-before-or-after-a-binary-operator)
style guide, which emphasizes that this approach improves readability.

This behaviour may raise `W503 line break before binary operator` warnings in style
guide enforcement tools like Flake8. Since `W503` is not PEP 8 compliant, you should
tell Flake8 to ignore these warnings.

### Slices

PEP 8
[recommends](https://www.python.org/dev/peps/pep-0008/#whitespace-in-expressions-and-statements)
to treat `:` in slices as a binary operator with the lowest priority, and to leave an
equal amount of space on either side, except if a parameter is omitted (e.g.
`ham[1 + 1 :]`). It recommends no spaces around `:` operators for "simple expressions"
(`ham[lower:upper]`), and extra space for "complex expressions"
(`ham[lower : upper + offset]`). _Black_ treats anything more than variable names as
"complex" (`ham[lower : upper + 1]`). It also states that for extended slices, both `:`
operators have to have the same amount of spacing, except if a parameter is omitted
(`ham[1 + 1 ::]`). _Black_ enforces these rules consistently.

This behaviour may raise `E203 whitespace before ':'` warnings in style guide
enforcement tools like Flake8. Since `E203` is not PEP 8 compliant, you should tell
Flake8 to ignore these warnings.

### Parentheses

Some parentheses are optional in the Python grammar. Any expression can be wrapped in a
pair of parentheses to form an atom. There are a few interesting cases:

- `if (...):`
- `while (...):`
- `for (...) in (...):`
- `assert (...), (...)`
- `from X import (...)`
- assignments like:
  - `target = (...)`
  - `target: type = (...)`
  - `some, *un, packing = (...)`
  - `augmented += (...)`

In those cases, parentheses are removed when the entire statement fits in one line, or
if the inner expression doesn't have any delimiters to further split on. If there is
only a single delimiter and the expression starts or ends with a bracket, the
parenthesis can also be successfully omitted since the existing bracket pair will
organize the expression neatly anyway. Otherwise, the parentheses are added.

Please note that _Black_ does not add or remove any additional nested parentheses that
you might want to have for clarity or further code organization. For example those
parentheses are not going to be removed:

```py3
return not (this or that)
decision = (maybe.this() and values > 0) or (maybe.that() and values < 0)
```

### Call chains

Some popular APIs, like ORMs, use call chaining. This API style is known as a
[fluent interface](https://en.wikipedia.org/wiki/Fluent_interface). _Black_ formats
those by treating dots that follow a call or an indexing operation like a very low
priority delimiter. It's easier to show the behavior than to explain it. Look at the
example:

```py3
def example(session):
    result = (
        session.query(models.Customer.id)
        .filter(
            models.Customer.account_id == account_id,
            models.Customer.email == email_address,
        )
        .order_by(models.Customer.id.asc())
        .all()
    )
```

### Typing stub files

PEP 484 describes the syntax for type hints in Python. One of the use cases for typing
is providing type annotations for modules which cannot contain them directly (they might
be written in C, or they might be third-party, or their implementation may be overly
dynamic, and so on).

To solve this,
[stub files with the `.pyi` file extension](https://www.python.org/dev/peps/pep-0484/#stub-files)
can be used to describe typing information for an external module. Those stub files omit
the implementation of classes and functions they describe, instead they only contain the
structure of the file (listing globals, functions, and classes with their members). The
recommended code style for those files is more terse than PEP 8:

- prefer `...` on the same line as the class/function signature;
- avoid vertical whitespace between consecutive module-level functions, names, or
  methods and fields within a single class;
- use a single blank line between top-level class definitions, or none if the classes
  are very small.

_Black_ enforces the above rules. There are additional guidelines for formatting `.pyi`
file that are not enforced yet but might be in a future version of the formatter:

- all function bodies should be empty (contain `...` instead of the body);
- do not use docstrings;
- prefer `...` over `pass`;
- for arguments with a default, use `...` instead of the actual default;
- avoid using string literals in type annotations, stub files support forward references
  natively (like Python 3.7 code with `from __future__ import annotations`);
- use variable annotations instead of type comments, even for stubs that target older
  versions of Python;
- for arguments that default to `None`, use `Optional[]` explicitly;
- use `float` instead of `Union[int, float]`.

## Pragmatism

Early versions of _Black_ used to be absolutist in some respects. They took after its
initial author. This was fine at the time as it made the implementation simpler and
there were not many users anyway. Not many edge cases were reported. As a mature tool,
_Black_ does make some exceptions to rules it otherwise holds. This section documents
what those exceptions are and why this is the case.

### The magic trailing comma

_Black_ in general does not take existing formatting into account.

However, there are cases where you put a short collection or function call in your code
but you anticipate it will grow in the future.

For example:

```py3
TRANSLATIONS = {
    "en_us": "English (US)",
    "pl_pl": "polski",
}
```

Early versions of _Black_ used to ruthlessly collapse those into one line (it fits!).
Now, you can communicate that you don't want that by putting a trailing comma in the
collection yourself. When you do, _Black_ will know to always explode your collection
into one item per line.

How do you make it stop? Just delete that trailing comma and _Black_ will collapse your
collection into one line if it fits.

### r"strings" and R"strings"

_Black_ normalizes string quotes as well as string prefixes, making them lowercase. One
exception to this rule is r-strings. It turns out that the very popular
[MagicPython](https://github.com/MagicStack/MagicPython/) syntax highlighter, used by
default by (among others) GitHub and Visual Studio Code, differentiates between
r-strings and R-strings. The former are syntax highlighted as regular expressions while
the latter are treated as true raw strings with no special semantics.
