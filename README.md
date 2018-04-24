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


## Installation and Usage

### Installation

*Black* can be installed by running `pip install black`.  It requires
Python 3.6.0+ to run but you can reformat Python 2 code with it, too.


### Usage

To get started right away with sensible defaults:

```
black {source_file_or_directory}
```

### Command line options

Black doesn't provide many options.  You can list them by running
`black --help`:

```text
black [OPTIONS] [SRC]...

Options:
  -l, --line-length INTEGER   Where to wrap around.  [default: 88]
  --check                     Don't write the files back, just return the
                              status.  Return code 0 means nothing would
                              change.  Return code 1 means some files would be
                              reformatted.  Return code 123 means there was an
                              internal error.
  --diff                      Don't write the files back, just output a diff
                              for each file on stdout.
  --fast / --safe             If --fast given, skip temporary sanity checks.
                              [default: --safe]
  -q, --quiet                 Don't emit non-error messages to stderr. Errors
                              are still emitted, silence those with
                              2>/dev/null.
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


### NOTE: This is an early pre-release

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


## The *Black* code style

*Black* reformats entire files in place.  It is not configurable.  It
doesn't take previous formatting into account.  It doesn't reformat
blocks that start with `# fmt: off` and end with `# fmt: on`.  It also
recognizes [YAPF](https://github.com/google/yapf)'s block comments to
the same effect, as a courtesy for straddling code.


### How *Black* wraps lines

*Black* ignores previous formatting and applies uniform horizontal
and vertical whitespace to your code.  The rules for horizontal
whitespace are pretty obvious and can be summarized as: do whatever
makes `pycodestyle` happy.  The coding style used by *Black* can be
viewed as a strict subset of PEP 8.

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
    with open(file, "w") as f:
        ...
```

You might have noticed that closing brackets are always dedented and
that a trailing comma is always added.  Such formatting produces smaller
diffs; when you add or remove an element, it's always just one line.
Also, having the closing bracket dedented provides a clear delimiter
between two distinct sections of the code that otherwise share the same
indentation level (like the arguments list and the docstring in the
example above).


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

*Black* avoids spurious vertical whitespace.  This is in the spirit of
PEP 8 which says that in-function vertical whitespace should only be
used sparingly.  One exception is control flow statements: *Black* will
always emit an extra empty line after ``return``, ``raise``, ``break``,
``continue``, and ``yield``.  This is to make changes in control flow
more prominent to readers of your code.

*Black* will allow single empty lines inside functions, and single and
double empty lines on module level left by the original editors, except
when they're within parenthesized expressions.  Since such expressions
are always reformatted to fit minimal space, this whitespace is lost.

It will also insert proper spacing before and after function definitions.
It's one line before and after inner functions and two lines before and
after module-level functions.  *Black* will put those empty lines also
between the function definition and any standalone comments that
immediately precede the given function.  If you want to comment on the
entire function, use a docstring or put a leading comment in the function
body.


### Trailing commas

*Black* will add trailing commas to expressions that are split
by comma where each element is on its own line.  This includes function
signatures.

Unnecessary trailing commas are removed if an expression fits in one
line.  This makes it 1% more likely that your line won't exceed the
allotted line length limit.  Moreover, in this scenario, if you added
another argument to your call, you'd probably fit it in the same line
anyway.  That doesn't make diffs any larger.

One exception to removing trailing commas is tuple expressions with
just one element.  In this case *Black* won't touch the single trailing
comma as this would unexpectedly change the underlying data type.  Note
that this is also the case when commas are used while indexing.  This is
a tuple in disguise: ```numpy_array[3, ]```.

One exception to adding trailing commas is function signatures
containing `*`, `*args`, or `**kwargs`.  In this case a trailing comma
is only safe to use on Python 3.6.  *Black* will detect if your file is
already 3.6+ only and use trailing commas in this situation.  If you
wonder how it knows, it looks for f-strings and existing use of trailing
commas in function signatures that have stars in them.  In other words,
if you'd like a trailing comma in this situation and *Black* didn't
recognize it was safe to do so, put it there manually and *Black* will
keep it.

### Strings

*Black* prefers double quotes (`"` and `"""`) over single quotes (`'`
and `'''`).  It will replace the latter with the former as long as it
does not result in more backslash escapes than before.

The main reason to standardize on a single form of quotes is aesthetics.
Having one kind of quotes everywhere reduces reader distraction.
It will also enable a future version of *Black* to merge consecutive
string literals that ended up on the same line (see
[#26](https://github.com/ambv/black/issues/26) for details).

Why settle on double quotes?  They anticipate apostrophes in English
text.  They match the docstring standard described in PEP 257.  An
empty string in double quotes (`""`) is impossible to confuse with
a one double-quote regardless of fonts and syntax highlighting used.
On top of this, double quotes for strings are consistent with C which
Python interacts a lot with.

On certain keyboard layouts like US English, typing single quotes is
a bit easier than double quotes.  The latter requires use of the Shift
key.  My recommendation here is to keep using whatever is faster to type
and let *Black* handle the transformation.

### Line Breaks & Binary Operators

*Black* will break a line before a binary operator when splitting a block
of code over multiple lines. This is so that *Black* is compliant with the
recent changes in the [PEP 8](https://www.python.org/dev/peps/pep-0008/#should-a-line-break-before-or-after-a-binary-operator)
style guide, which emphasizes that this approach improves readability.

This behaviour may raise ``W503 line break before binary operator`` warnings in
style guide enforcement tools like Flake8. Since ``W503`` is not PEP 8 compliant,
you should tell Flake8 to ignore these warnings.

### Parentheses

Some parentheses are optional in the Python grammar.  Any expression can
be wrapped in a pair of parentheses to form an atom.  There are a few
interesting cases:

- `if (...):`
- `while (...):`
- `for (...) in (...):`
- `assert (...), (...)`
- `from X import (...)`

In those cases, parentheses are removed when the entire statement fits
in one line, or if the inner expression doesn't have any delimiters to
further split on.  Otherwise, the parentheses are always added.


## Editor integration

### Emacs

Use [proofit404/blacken](https://github.com/proofit404/blacken).


### PyCharm

1. Install `black`.

        $ pip install black

2. Locate your `black` installation folder.

  On MacOS / Linux / BSD:

        $ which black
        /usr/local/bin/black  # possible location

  On Windows:

        $ where black
        %LocalAppData%\Programs\Python\Python36-32\Scripts\black.exe  # possible location

3. Open External tools in PyCharm with `File -> Settings -> Tools -> External Tools`.

4. Click the + icon to add a new external tool with the following values:
    - Name: Black
    - Description: Black is the uncompromising Python code formatter.
    - Program: <install_location_from_step_2>
    - Arguments: $FilePath$

5. Format the currently opened file by selecting `Tools -> External Tools -> black`.
    - Alternatively, you can set a keyboard shortcut by navigating to `Preferences -> Keymap`.


### Vim

Commands and shortcuts:

* `,=` or `:Black` to format the entire file (ranges not supported);
* `:BlackUpgrade` to upgrade *Black* inside the virtualenv;
* `:BlackVersion` to get the current version of *Black* inside the
  virtualenv.

Configuration:
* `g:black_fast` (defaults to `0`)
* `g:black_linelength` (defaults to `88`)
* `g:black_virtualenv` (defaults to `~/.vim/black`)

To install with [vim-plug](https://github.com/junegunn/vim-plug):

```
Plug 'ambv/black',
```

or with [Vundle](https://github.com/VundleVim/Vundle.vim):

```
Plugin 'ambv/black'
```

or you can copy the plugin from [plugin/black.vim](https://github.com/ambv/black/tree/master/plugin/black.vim).
Let me know if this requires any changes to work with Vim 8's builtin
`packadd`, or Pathogen, and so on.

This plugin **requires Vim 7.0+ built with Python 3.6+ support**.  It
needs Python 3.6 to be able to run *Black* inside the Vim process which
is much faster than calling an external command.

On first run, the plugin creates its own virtualenv using the right
Python version and automatically installs *Black*. You can upgrade it later
by calling `:BlackUpgrade` and restarting Vim.

If you need to do anything special to make your virtualenv work and
install *Black* (for example you want to run a version from master), just
create a virtualenv manually and point `g:black_virtualenv` to it.
The plugin will use it.

**How to get Vim with Python 3.6?**
On Ubuntu 17.10 Vim comes with Python 3.6 by default.
On macOS with HomeBrew run: `brew install vim --with-python3`.
When building Vim from source, use:
`./configure --enable-python3interp=yes`. There's many guides online how
to do this.


### Visual Studio Code

Use [joslarson.black-vscode](https://marketplace.visualstudio.com/items?itemName=joslarson.black-vscode).

### SublimeText 3

Use [sublack plugin](https://github.com/jgirardet/sublack).

### Other editors

Atom/Nuclide integration is planned by the author, others will
require external contributions.

Patches welcome! ✨ 🍰 ✨

Any tool that can pipe code through *Black* using its stdio mode (just
[use `-` as the file name](http://www.tldp.org/LDP/abs/html/special-chars.html#DASHREF2)).
The formatted code will be returned on stdout (unless `--check` was
passed).  *Black* will still emit messages on stderr but that shouldn't
affect your use case.

This can be used for example with PyCharm's [File Watchers](https://www.jetbrains.com/help/pycharm/file-watchers.html).


## Version control integration

Use [pre-commit](https://pre-commit.com/). Once you [have it
installed](https://pre-commit.com/#install), add this to the
`.pre-commit-config.yaml` in your repository:
```yaml
repos:
-   repo: https://github.com/ambv/black
    rev: stable
    hooks:
    - id: black
      args: [--line-length=88, --safe]
      python_version: python3.6
```
Then run `pre-commit install` and you're ready to go.

`args` in the above config is optional but shows you how you can change
the line length if you really need to.  If you're already using Python
3.7, switch the `python_version` accordingly. Finally, `stable` is a tag
that is pinned to the latest release on PyPI.  If you'd rather run on
master, this is also an option.


## Ignoring non-modified files

*Black* remembers files it already formatted, unless the `--diff` flag is used or
code is passed via standard input. This information is stored per-user. The exact
location of the file depends on the black version and the system on which black
is run. The file is non-portable. The standard location on common operating systems
is:

* Windows: `C:\\Users\<username>\AppData\Local\black\black\Cache\<version>\cache.pickle`
* macOS: `/Users/<username>/Library/Caches/black/<version>/cache.pickle`
* Linux: `/home/<username>/.cache/black/<version>/cache.pickle`


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


## Contributing to Black

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

### 18.4a3 (unreleased)

* added a "cache"; files already reformatted that haven't changed on disk
  won't be reformatted again (#109)

* `--check` and `--diff` are no longer mutually exclusive (#149)

* generalized star expression handling, including double stars; this
  fixes multiplication making expressions "unsafe" for trailing commas (#132)

* fixed comment indentation when a standalone comment closes a block (#16, #32)

* fixed `--diff` not showing entire path (#130)

* fixed parsing of complex expressions after star and double stars in
  function calls (#2)

* fixed invalid splitting on comma in lambda arguments (#133)

### 18.4a2

* fixed parsing of unaligned standalone comments (#99, #112)

* fixed placement of dictionary unpacking inside dictionary literals (#111)

* Vim plugin now works on Windows, too

* fixed unstable formatting when encountering unnecessarily escaped quotes
  in a string (#120)


### 18.4a1

* added `--quiet` (#78)

* added automatic parentheses management (#4)

* added [pre-commit](https://pre-commit.com) integration (#103, #104)

* fixed reporting on `--check` with multiple files (#101, #102)

* fixed removing backslash escapes from raw strings (#100, #105)


### 18.4a0

* added `--diff` (#87)

* add line breaks before all delimiters, except in cases like commas, to
  better comply with PEP 8 (#73)

* standardize string literals to use double quotes (almost) everywhere
  (#75)

* fixed handling of standalone comments within nested bracketed
  expressions; Black will no longer produce super long lines or put all
  standalone comments at the end of the expression (#22)

* fixed 18.3a4 regression: don't crash and burn on empty lines with
  trailing whitespace (#80)

* fixed 18.3a4 regression: `# yapf: disable` usage as trailing comment
  would cause Black to not emit the rest of the file (#95)

* when CTRL+C is pressed while formatting many files, Black no longer
  freaks out with a flurry of asyncio-related exceptions

* only allow up to two empty lines on module level and only single empty
  lines within functions (#74)


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

Maintained with [Carol Willing](mailto:carolcode@willingconsulting.com),
[Carl Meyer](mailto:carl@oddbird.net),
[Mika Naylor](mailto:mail@autophagy.io), and
[Zsolt Dollenstein](mailto:zsol.zsol@gmail.com).

Multiple contributions by:
* [Anthony Sottile](mailto:asottile@umich.edu)
* [Artem Malyshev](mailto:proofit404@gmail.com)
* [Daniel M. Capella](mailto:polycitizen@gmail.com)
* [Eli Treuherz](mailto:eli.treuherz@cgi.com)
* Hugo van Kemenade
* [Ivan Katanić](mailto:ivan.katanic@gmail.com)
* [Jonas Obrist](mailto:ojiidotch@gmail.com)
* [Osaetin Daniel](mailto:osaetindaniel@gmail.com)
* [Vishwas B Sharma](mailto:sharma.vishwas88@gmail.com)
