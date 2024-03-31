# The basics

An overview on contributing to the _Black_ project.

## Technicalities

Development on the latest version of Python is preferred. You can use any operating
system.

Install development dependencies inside a virtual environment of your choice, for
example:

```console
$ python3 -m venv .venv
$ source .venv/bin/activate # activation for linux and mac
$ .venv\Scripts\activate # activation for windows

(.venv)$ pip install -r test_requirements.txt
(.venv)$ pip install -e .[d]
(.venv)$ pre-commit install
```

Before submitting pull requests, run lints and tests with the following commands from
the root of the black repo:

```console
# Linting
(.venv)$ pre-commit run -a

# Unit tests
(.venv)$ tox -e py

# Optional Fuzz testing
(.venv)$ tox -e fuzz

# Format Black itself
(.venv)$ tox -e run_self
```

### Development

Further examples of invoking the tests

```console
# Run all of the above mentioned, in parallel
(.venv)$ tox --parallel=auto

# Run tests on a specific python version
(.venv)$ tox -e py39

# pass arguments to pytest
(.venv)$ tox -e py -- --no-cov

# print full tree diff, see documentation below
(.venv)$ tox -e py -- --print-full-tree

# disable diff printing, see documentation below
(.venv)$ tox -e py -- --print-tree-diff=False
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
are split into an input part, and an output part, separated by a line with`# output`.
These can be passed to `pytest` through `tox`, or directly into pytest if not using
`tox`.

#### `--print-full-tree`

Upon a failing test, print the full concrete syntax tree (CST) as it is after processing
the input ("actual"), and the tree that's yielded after parsing the output ("expected").
Note that a test can fail with different output with the same CST. This used to be the
default, but now defaults to `False`.

#### `--print-tree-diff`

Upon a failing test, print the diff of the trees as described above. This is the
default. To turn it off pass `--print-tree-diff=False`.

### News / Changelog Requirement

`Black` has CI that will check for an entry corresponding to your PR in `CHANGES.md`. If
you feel this PR does not require a changelog entry please state that in a comment and a
maintainer can add a `skip news` label to make the CI pass. Otherwise, please ensure you
have a line in the following format:

```md
- `Black` is now more awesome (#X)
```

Note that X should be your PR number, not issue number! To workout X, please use
[Next PR Number](https://ichard26.github.io/next-pr-number/?owner=psf&name=black). This
is not perfect but saves a lot of release overhead as now the releaser does not need to
go back and workout what to add to the `CHANGES.md` for each release.

### Style Changes

If a change would affect the advertised code style, please modify the documentation (The
_Black_ code style) to reflect that change. Patches that fix unintended bugs in
formatting don't need to be mentioned separately though. If the change is implemented
with the `--preview` flag, please include the change in the future style document
instead and write the changelog entry under a dedicated "Preview changes" heading.

### Docs Testing

If you make changes to docs, you can test they still build locally too.

```console
(.venv)$ pip install -r docs/requirements.txt
(.venv)$ pip install -e .[d]
(.venv)$ sphinx-build -a -b html -W docs/ docs/_build/
```

## Hygiene

If you're fixing a bug, add a test. Run it first to confirm it fails, then fix the bug,
run it again to confirm it's really fixed.

If adding a new feature, add a test. In fact, always add a test. But wait, before adding
any large feature, first open an issue for us to discuss the idea first.

## Finally

Thanks again for your interest in improving the project! You're taking action when most
people decide to sit and watch.
