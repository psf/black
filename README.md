![Black Logo](https://raw.githubusercontent.com/ambv/black/master/docs/_static/logo2-readme.png)
<h2 align="center">The Uncompromising Code Formatter</h2>

<p align="center">
<a href="https://travis-ci.org/ambv/black"><img alt="Build Status" src="https://travis-ci.org/ambv/black.svg?branch=master"></a>
<a href="http://black.readthedocs.io/en/latest/?badge=latest"><img alt="Documentation Status" src="http://readthedocs.org/projects/black/badge/?version=latest"></a>
<a href="https://coveralls.io/github/ambv/black?branch=master"><img alt="Coverage Status" src="https://coveralls.io/repos/github/ambv/black/badge.svg?branch=master"></a>
<a href="https://github.com/ambv/black/blob/master/LICENSE"><img alt="License: MIT" src="http://black.readthedocs.io/en/latest/_static/license.svg"></a>
<a href="https://pypi.python.org/pypi/black"><img alt="PyPI" src="http://black.readthedocs.io/en/latest/_static/pypi.svg"></a>
<a href="https://github.com/ambv/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

> “Any color you like.”


*Black* is the uncompromising Python code formatter.  By using it, you
agree to cease control over minutiae of hand-formatting.  In return,
*Black* gives you speed, determinism, and freedom from `pycodestyle`
nagging about formatting.  You will save time and mental energy for
more important matters.

Blackened code looks the same regardless of the project you're reading.
Formatting becomes transparent after a while and you can focus on the
content instead.

*Black* makes code review faster by producing the smallest diffs
possible.


## NOTE: This is an early pre-release

*Black* can already successfully format itself and the standard library.
It also sports a decent test suite.  However, it is still very new.
Things will probably be wonky for a while. This is made explicit by the
"Alpha" trove classifier, as well as by the "a" in the version number.
What this means for you is that **until the formatter becomes stable,
you should expect some formatting to change in the future**.

Also, as a temporary safety measure, *Black* will check that the
reformatted code still produces a valid AST that is equivalent to the
original.  This slows it down.  If you're feeling confident, use
``--fast``.


## Installation

*Black* can be installed by running `pip install black`.  It requires
Python 3.6.0+ to run but you can reformat Python 2 code with it, too.
*Black* is able to parse all of the new syntax supported on Python 3.6
but also *effectively all* the Python 2 syntax at the same time.


## Usage


```
black [OPTIONS] [SRC]...

Options:
  -l, --line-length INTEGER   Where to wrap around.  [default: 88]
  --check                     Don't write back the files, just return the
                              status.  Return code 0 means nothing would
                              change.  Return code 1 means some files would be
                              reformatted.  Return code 123 means there was an
                              internal error.
  --fast / --safe             If --fast given, skip temporary sanity checks.
                              [default: --safe]
  --version                   Show the version and exit.
  --help                      Show this message and exit.
```

*Black* is a well-behaved Unix-style command-line tool:
* it does nothing if no sources are passed to it;
* it will read from standard input and write to standard output if `-`
  is used as the filename;
* it only outputs messages to users on standard error;
* exits with code 0 unless an internal error occured (or `--check` was
  used).


## The philosophy behind *Black*

*Black* reformats entire files in place.  It is not configurable.  It
doesn't take previous formatting into account.  It doesn't reformat
blocks that start with `# fmt: off` and end with `# fmt: on`.  It also
recognizes [YAPF](https://github.com/google/yapf)'s block comments to
the same effect, as a courtesy for straddling code.


### How *Black* formats files

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


### Line length

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


### Empty lines

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


### Editor integration

* Visual Studio Code: [joslarson.black-vscode](https://marketplace.visualstudio.com/items?itemName=joslarson.black-vscode)
* Emacs: [proofit404/blacken](https://github.com/proofit404/blacken)

Any tool that can pipe code through *Black* using its stdio mode (just
[use `-` as the file name](http://www.tldp.org/LDP/abs/html/special-chars.html#DASHREF2)).
The formatted code will be returned on stdout (unless `--check` was
passed).  *Black* will still emit messages on stderr but that shouldn't
affect your use case.

Vim and Atom/Nuclide integration is planned by the author, others will
require external contributions.

Patches welcome! ✨ 🍰 ✨


## Testimonials

**Dusty Phillips**, [writer](https://smile.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=dusty+phillips):

> Black is opinionated so you don't have to be.

**Hynek Schlawack**, [creator of `attrs`](http://www.attrs.org/), core
developer of Twisted and CPython:

> An auto-formatter that doesn't suck is all I want for Xmas!

**Carl Meyer**, [Django](https://www.djangoproject.com/) core developer:

> At least the name is good.

**Kenneth Reitz**, creator of [`requests`](http://python-requests.org/)
and [`pipenv`](https://docs.pipenv.org/):

> This vastly improves the formatting of our code. Thanks a ton!


## Show your style

Use the badge in your project's README.md:

```markdown
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
```

Looks like this: [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


## License

MIT


## Contributing

In terms of inspiration, *Black* is about as configurable as *gofmt* and
*rustfmt* are.  This is deliberate.

Bug reports and fixes are always welcome!  However, before you suggest a
new feature or configuration knob, ask yourself why you want it.  If it
enables better integration with some workflow, fixes an inconsistency,
speeds things up, and so on - go for it!  On the other hand, if your
answer is "because I don't like a particular formatting" then you're not
ready to embrace *Black* yet. Such changes are unlikely to get accepted.
You can still try but prepare to be disappointed.

More details can be found in [CONTRIBUTING](CONTRIBUTING.md).


## Change Log

### 18.3a4

* `# fmt: off` and `# fmt: on` are implemented (#5)

* automatic detection of deprecated Python 2 forms of print statements
  and exec statements in the formatted file (#49)

* use proper spaces for complex expressions in default values of typed
  function arguments (#60)

* only return exit code 1 when --check is used (#50)

* don't remove single trailing commas from square bracket indexing
  (#59)

* don't omit whitespace if the previous factor leaf wasn't a math
  operator (#55)

* omit extra space in kwarg unpacking if it's the first argument (#46)

* omit extra space in [Sphinx auto-attribute comments](http://www.sphinx-doc.org/en/stable/ext/autodoc.html#directive-autoattribute)
  (#68)


### 18.3a3

* don't remove single empty lines outside of bracketed expressions
  (#19)

* added ability to pipe formatting from stdin to stdin (#25)

* restored ability to format code with legacy usage of `async` as
  a name (#20, #42)

* even better handling of numpy-style array indexing (#33, again)


### 18.3a2

* changed positioning of binary operators to occur at beginning of lines
  instead of at the end, following [a recent change to PEP8](https://github.com/python/peps/commit/c59c4376ad233a62ca4b3a6060c81368bd21e85b)
  (#21)

* ignore empty bracket pairs while splitting. This avoids very weirdly
  looking formattings (#34, #35)

* remove a trailing comma if there is a single argument to a call

* if top level functions were separated by a comment, don't put four
  empty lines after the upper function

* fixed unstable formatting of newlines with imports

* fixed unintentional folding of post scriptum standalone comments
  into last statement if it was a simple statement (#18, #28)

* fixed missing space in numpy-style array indexing (#33)

* fixed spurious space after star-based unary expressions (#31)


### 18.3a1

* added `--check`

* only put trailing commas in function signatures and calls if it's
  safe to do so. If the file is Python 3.6+ it's always safe, otherwise
  only safe if there are no `*args` or `**kwargs` used in the signature
  or call. (#8)

* fixed invalid spacing of dots in relative imports (#6, #13)

* fixed invalid splitting after comma on unpacked variables in for-loops
  (#23)

* fixed spurious space in parenthesized set expressions (#7)

* fixed spurious space after opening parentheses and in default
  arguments (#14, #17)

* fixed spurious space after unary operators when the operand was
  a complex expression (#15)


### 18.3a0

* first published version, Happy 🍰 Day 2018!

* alpha quality

* date-versioned (see: https://calver.org/)


## Authors

Glued together by [Łukasz Langa](mailto:lukasz@langa.pl).
