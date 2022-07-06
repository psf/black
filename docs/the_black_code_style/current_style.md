# The _Black_ code style

## Code style

_Black_ aims for consistency, generality, readability and reducing git diffs. Similar
language constructs are formatted with similar rules. Style configuration options are
deliberately limited and rarely added. Previous formatting is taken into account as
little as possible, with rare exceptions like the magic trailing comma. The coding style
used by _Black_ can be viewed as a strict subset of PEP 8.

_Black_ reformats entire files in place. It doesn't reformat lines that end with
`# fmt: skip` or blocks that start with `# fmt: off` and end with `# fmt: on`.
`# fmt: on/off` must be on the same level of indentation and in the same block, meaning
no unindents beyond the initial indentation level between them. It also recognizes
[YAPF](https://github.com/google/yapf)'s block comments to the same effect, as a
courtesy for straddling code.

The rest of this document describes the current formatting style. If you're interested
in trying out where the style is heading, see [future style](./future_style.md) and try
running `black --preview`.

### How _Black_ wraps lines

_Black_ ignores previous formatting and applies uniform horizontal and vertical
whitespace to your code. The rules for horizontal whitespace can be summarized as: do
whatever makes `pycodestyle` happy.

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

(labels/why-no-backslashes)=

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

You might have noticed that closing brackets are always dedented and that a trailing
comma is always added. Such formatting produces smaller diffs; when you add or remove an
element, it's always just one line. Also, having the closing bracket dedented provides a
clear delimiter between two distinct sections of the code that otherwise share the same
indentation level (like the arguments list and the docstring in the example above).

If a data structure literal (tuple, list, set, dict) or a line of "from" imports cannot
fit in the allotted length, it's always split into one element per line. This minimizes
diffs as well as enables readers of code to find which commit introduced a particular
entry. This also makes _Black_ compatible with
[isort](../guides/using_black_with_other_tools.md#isort) with the ready-made `black`
profile or manual configuration.

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

If you're using Flake8, you can bump `max-line-length` to 88 and mostly forget about it.
However, it's better if you use [Bugbear](https://github.com/PyCQA/flake8-bugbear)'s
B950 warning instead of E501, and bump the max line length to 88 (or the `--line-length`
you used for black), which will align more with black's _"try to respect
`--line-length`, but don't become crazy if you can't"_. You'd do it like this:

```ini
[flake8]
max-line-length = 88
...
select = C,E,F,W,B,B950
extend-ignore = E203, E501
```

Explanation of why E203 is disabled can be found further in this documentation. And if
you're curious about the reasoning behind B950,
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

### Comments

_Black_ does not format comment contents, but it enforces two spaces between code and a
comment on the same line, and a space before the comment text begins. Some types of
comments that require specific spacing rules are respected: doc comments (`#: comment`),
section comments with long runs of hashes, and Spyder cells. Non-breaking spaces after
hashes are also preserved. Comments may sometimes be moved because of formatting
changes, which can break tools that assign special meaning to them. See
[AST before and after formatting](#ast-before-and-after-formatting) for more discussion.

### Trailing commas

_Black_ will add trailing commas to expressions that are split by comma where each
element is on its own line. This includes function signatures.

One exception to adding trailing commas is function signatures containing `*`, `*args`,
or `**kwargs`. In this case a trailing comma is only safe to use on Python 3.6. _Black_
will detect if your file is already 3.6+ only and use trailing commas in this situation.
If you wonder how it knows, it looks for f-strings and existing use of trailing commas
in function signatures that have stars in them. In other words, if you'd like a trailing
comma in this situation and _Black_ didn't recognize it was safe to do so, put it there
manually and _Black_ will keep it.

A pre-existing trailing comma informs _Black_ to always explode contents of the current
bracket pair into one item per line. Read more about this in the
[Pragmatism](#pragmatism) section below.

### Strings

_Black_ prefers double quotes (`"` and `"""`) over single quotes (`'` and `'''`). It
will replace the latter with the former as long as it does not result in more backslash
escapes than before.

_Black_ also standardizes string prefixes. Prefix characters are made lowercase with the
exception of [capital "R" prefixes](#rstrings-and-rstrings), unicode literal markers
(`u`) are removed because they are meaningless in Python 3, and in the case of multiple
characters "r" is put first as in spoken language: "raw f-string".

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

_Black_ also processes docstrings. Firstly the indentation of docstrings is corrected
for both quotations and the text within, although relative indentation in the text is
preserved. Superfluous trailing whitespace on each line and unnecessary new lines at the
end of the docstring are removed. All leading tabs are converted to spaces, but tabs
inside text are preserved. Whitespace leading and trailing one-line docstrings is
removed.

### Numeric literals

_Black_ standardizes most numeric literals to use lowercase letters for the syntactic
parts and uppercase letters for the digits themselves: `0xAB` instead of `0XAB` and
`1e10` instead of `1E10`.

### Line breaks & binary operators

_Black_ will break a line before a binary operator when splitting a block of code over
multiple lines. This is so that _Black_ is compliant with the recent changes in the
[PEP 8](https://www.python.org/dev/peps/pep-0008/#should-a-line-break-before-or-after-a-binary-operator)
style guide, which emphasizes that this approach improves readability.

Almost all operators will be surrounded by single spaces, the only exceptions are unary
operators (`+`, `-`, and `~`), and power operators when both operands are simple. For
powers, an operand is considered simple if it's only a NAME, numeric CONSTANT, or
attribute access (chained attribute access is allowed), with or without a preceding
unary operator.

```python
# For example, these won't be surrounded by whitespace
a = x**y
b = config.base**5.2
c = config.base**runtime.config.exponent
d = 2**5
e = 2**~5

# ... but these will be surrounded by whitespace
f = 2 ** get_exponent()
g = get_x() ** get_y()
h = config['base'] ** 2
```

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
parentheses can also be successfully omitted since the existing bracket pair will
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

- prefer `...` over `pass`;
- avoid using string literals in type annotations, stub files support forward references
  natively (like Python 3.7 code with `from __future__ import annotations`);
- use variable annotations instead of type comments, even for stubs that target older
  versions of Python.

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

If you must, you can recover the behaviour of early versions of _Black_ with the option
`--skip-magic-trailing-comma` / `-C`.

### r"strings" and R"strings"

_Black_ normalizes string quotes as well as string prefixes, making them lowercase. One
exception to this rule is r-strings. It turns out that the very popular
[MagicPython](https://github.com/MagicStack/MagicPython/) syntax highlighter, used by
default by (among others) GitHub and Visual Studio Code, differentiates between
r-strings and R-strings. The former are syntax highlighted as regular expressions while
the latter are treated as true raw strings with no special semantics.

### AST before and after formatting

When run with `--safe`, _Black_ checks that the code before and after is semantically
equivalent. This check is done by comparing the AST of the source with the AST of the
target. There are three limited cases in which the AST does differ:

1. _Black_ cleans up leading and trailing whitespace of docstrings, re-indenting them if
   needed. It's been one of the most popular user-reported features for the formatter to
   fix whitespace issues with docstrings. While the result is technically an AST
   difference, due to the various possibilities of forming docstrings, all realtime use
   of docstrings that we're aware of sanitizes indentation and leading/trailing
   whitespace anyway.

1. _Black_ manages optional parentheses for some statements. In the case of the `del`
   statement, presence of wrapping parentheses or lack of thereof changes the resulting
   AST but is semantically equivalent in the interpreter.

1. _Black_ might move comments around, which includes type comments. Those are part of
   the AST as of Python 3.8. While the tool implements a number of special cases for
   those comments, there is no guarantee they will remain where they were in the source.
   Note that this doesn't change runtime behavior of the source code.

To put things in perspective, the code equivalence check is a feature of _Black_ which
other formatters don't implement at all. It is of crucial importance to us to ensure
code behaves the way it did before it got reformatted. We treat this as a feature and
there are no plans to relax this in the future. The exceptions enumerated above stem
from either user feedback or implementation details of the tool. In each case we made
due diligence to ensure that the AST divergence is of no practical consequence.
