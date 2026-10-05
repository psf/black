# Contributing Basics

An overview on contributing to the _Black_ project.

If you are making a large change, please first open an issue to discuss it beforehand.

## Overview

Development on the latest version of Python is preferred. You can use any operating
system.

First clone the _Black_ repository:

```console
$ git clone https://github.com/psf/black.git
$ cd black
```

Then install development dependencies inside a virtual environment of your choice, for
example:

```console
$ python3 -m venv .venv
$ source .venv/bin/activate # activation for linux and mac
$ .venv\Scripts\activate # activation for windows

(.venv)$ pip install --group dev
(.venv)$ pip install -e ".[d]"
(.venv)$ pre-commit install
```

Before submitting pull requests, run lints and tests with the following commands from
the root of the black repo:

```console
(.venv)$ tox -e run_self # Format Black itself (required!)
(.venv)$ pre-commit run -a # Linting
(.venv)$ tox -e py # Unit tests (also run by CI)
(.venv)$ tox -e fuzz # Fuzz testing (optional)

(.venv)$ tox --parallel=auto # Run format, tests, and fuzz in parallel
```

## News / Changelog Requirement

`Black` has CI that will check for an entry corresponding to your PR in `CHANGES.md`. If
you feel your PR does not require a changelog entry, please state that in a comment and
a maintainer can add a `ci: skip news` label bypass the check. Otherwise, please ensure
you have a line in the following format added below the appropriate header:

```md
- `Black` is now more awesome (#X)
```

Note that X should be your PR number, not issue number! To workout X, please use
[Next PR Number](https://ichard26.github.io/next-pr-number/?owner=psf&name=black).

The description should be no more than two sentances and should accurately describe the
user-facing change. Avoid referencing Black internals or the implementation details of
the change.

This saves a lot of release overhead as the releaser does not need to work out what to
add to the `CHANGES.md` for each commit.

## Style Changes

Please familiarize yourself with our [stability policy](labels/stability-policy). Most
style changes must be added to the `--preview` style. Exceptions are fixing crashes or
changes that would not affect an already-formatted file.

If a change would affect the advertised code style, please modify
[the documentation](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html)
to reflect that change. Patches that fix unintended bugs in formatting don't need to be
mentioned separately.

If the change is implemented with the `--preview` or `--unstable` flag, please include
the change in the
[Future Style document](https://black.readthedocs.io/en/stable/the_black_code_style/future_style.html)
instead. Additionally, please ensure you include the changelog entry under the dedicated
"Preview style" heading.

## Testing

All aspects of the _Black_ style should be tested. PRs are welcome to add tests for
parts of Black that aren't covered by existing tests. Additionally, if you come across a
resolved but unclosed issue, please PR test cases for it before we close it, if they
don't exist already.

It's a good practice to follow Test-Driven Development: If you're fixing a bug, first
add a test. Run it to confirm it fails, then fix the bug, and run the test again to
confirm it's really fixed. Please add tests for any and all changes you make.

Whenever possible, tests should be created as files in the `tests/data/cases` directory.
These files consist of up to three parts:

- A line that starts with `# flags: ` followed by a set of command-line options. For
  example, if the line is `# flags: --preview --skip-magic-trailing-comma`, the test
  case will be run with preview mode on and the magic trailing comma off. The options
  accepted are mostly a subset of those of _Black_ itself, except for the
  `--minimum-version=` flag, which should be used when testing a grammar feature that
  works only in newer versions of Python. This flag ensures that we don't try to
  validate the AST on older versions and tests that we autodetect the Python version
  correctly when the feature is used. For the exact flags accepted, see the function
  `get_flags_parser` in `tests/util.py`. If this line is omitted, the default options
  are used.
- A block of Python code used as input for the formatter.
- The line `# output`, followed by the output of _Black_ when run on the previous block.
  If this is omitted, the test asserts that _Black_ will leave the input code unchanged.

### Test Arguments

Run tests on a specific python version:

```console
(.venv)$ tox -e py314
```

Run an individual test:

```console
(.venv)$ pytest -k <test name>
```

Pass arguments to pytest:

```console
(.venv)$ tox -e py -- --no-cov
```

_Black_ also has two unique CLI options that serve to help depug failing test files in
`tests/data/`. These can be passed to `pytest` through `tox` as shown above, or directly
into pytest if not using `tox`.

`--print-full-tree` prints the full concrete syntax tree (CST) upon a failing test. Both
the CST after parsing the input ("actual") and the CST after parsing the output
("expected") are printed. Note that a test can fail with different formatting outputs
but the same CST.

```console
(.venv)$ tox -e py -- --print-full-tree
```

`--print-tree-diff` prints the diff of the two CSTs described above upon a failing test.
This is the default. To turn it off pass `--print-tree-diff=False`.

```console
(.venv)$ tox -e py -- --print-tree-diff=False
```

## Docs Testing

If you make changes to docs, you can test they still build locally:

```console
(.venv)$ pip install --group docs
(.venv)$ pip install -e ".[d]"
(.venv)$ sphinx-build -a -b html -W docs/ docs/_build/
```

## Thank You!

Thanks again for your interest in improving the project! You're taking action when most
people decide to sit and watch.
