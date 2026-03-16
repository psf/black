# The basics

An overview on contributing to the _Black_ project.

## Technicalities

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
(.venv)$ pre-commit run -a # Linting
(.venv)$ tox -e py # Unit tests
(.venv)$ tox -e fuzz # Optional Fuzz testing
(.venv)$ tox -e run_self # Format Black itself
```

### Development

Further examples of invoking the tests

```console
(.venv)$ tox --parallel=auto # Run all the above in parallel
(.venv)$ tox -e py314 # Run tests on a specific python version
(.venv)$ pytest -k <test name> # Run an individual test
(.venv)$ tox -e py -- --no-cov # Pass arguments to pytest
```

### Testing

All aspects of the _Black_ style should be tested. Normally, tests should be created as
files in the `tests/data/cases` directory. These files consist of up to three parts:

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

_Black_ has two pytest command-line options affecting test files in `tests/data/` that
are split into an input part, and an output part, separated by a line with `# output`.
These can be passed to `pytest` through `tox`, or directly into pytest if not using
`tox`.

#### `--print-full-tree`

Upon a failing test, print the full concrete syntax tree (CST) as it is after processing
the input ("actual"), and the tree that's yielded after parsing the output ("expected").
Note that a test can fail with different output with the same CST. This used to be the
default, but now defaults to `False`.

```console
(.venv)$ tox -e py -- --print-full-tree
```

#### `--print-tree-diff`

Upon a failing test, print the diff of the trees as described above. This is the
default. To turn it off pass `--print-tree-diff=False`.

```console
(.venv)$ tox -e py -- --print-tree-diff=False
```

### News / Changelog Requirement

`Black` has CI that will check for an entry corresponding to your PR in `CHANGES.md`. If
you feel this PR does not require a changelog entry please state that in a comment and a
maintainer can add a `ci: skip news` label to make the CI pass. Otherwise, please ensure
you have a line in the following format added below the appropriate header:

```md
- `Black` is now more awesome (#X)
```

<!---
The Next PR Number link uses HTML because of a bug in MyST-Parser that double-escapes the ampersand, causing the query parameters to not be processed.
MyST-Parser issue: https://github.com/executablebooks/MyST-Parser/issues/760
MyST-Parser stalled fix PR: https://github.com/executablebooks/MyST-Parser/pull/929
-->

Note that X should be your PR number, not issue number! To workout X, please use
<a href="https://ichard26.github.io/next-pr-number/?owner=psf&name=black">Next PR
Number</a>. This is not perfect but saves a lot of release overhead as now the releaser
does not need to go back and workout what to add to the `CHANGES.md` for each release.

### Style Changes

Please familiarize yourself with our [stability policy](labels/stability-policy).
Therefore, most style changes must be added to the `--preview` style. Exceptions are
fixing crashes or changes that would not affect an already-formatted file.

If a change would affect the advertised code style, please modify the documentation (The
_Black_ code style) to reflect that change. Patches that fix unintended bugs in
formatting don't need to be mentioned separately.

If the change is implemented with the `--preview` flag, please include the change in the
Future Style document instead and write the changelog entry under the dedicated "Preview
style" heading.

### Docs Testing

If you make changes to docs, you can test they still build locally too.

```console
(.venv)$ pip install --group docs
(.venv)$ pip install -e ".[d]"
(.venv)$ sphinx-build -a -b html -W docs/ docs/_build/
```

## Hygiene

If you're fixing a bug, add a test. Run it first to confirm it fails, then fix the bug,
and run the test again to confirm it's really fixed.

If adding a new feature, add a test. In fact, always add a test. If adding a large
feature, please first open an issue to discuss it beforehand.

## Finally

Thanks again for your interest in improving the project! You're taking action when most
people decide to sit and watch.
