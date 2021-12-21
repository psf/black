# The basics

An overview on contributing to the _Black_ project.

## Technicalities

Development on the latest version of Python is preferred. As of this writing it's 3.9.
You can use any operating system.

Install development dependencies inside a virtual environment of your choice, for
example:

```console
$ python3 -m venv .venv
$ source .venv/bin/activate
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

# Optional CI run to test your changes on many popular python projects
(.venv)$ black-primer [-k -w /tmp/black_test_repos]
```

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
formatting don't need to be mentioned separately though.

### Docs Testing

If you make changes to docs, you can test they still build locally too.

```console
(.venv)$ pip install -r docs/requirements.txt
(.venv)$ pip install [-e] .[d]
(.venv)$ sphinx-build -a -b html -W docs/ docs/_build/
```

## black-primer

`black-primer` is used by CI to pull down well-known _Black_ formatted projects and see
if we get source code changes. It will error on formatting changes or errors. Please run
before pushing your PR to see if you get the actions you would expect from _Black_ with
your PR. You may need to change
[primer.json](https://github.com/psf/black/blob/main/src/black_primer/primer.json)
configuration for it to pass.

For more `black-primer` information visit the
[documentation](./gauging_changes.md#black-primer).

## Hygiene

If you're fixing a bug, add a test. Run it first to confirm it fails, then fix the bug,
run it again to confirm it's really fixed.

If adding a new feature, add a test. In fact, always add a test. But wait, before adding
any large feature, first open an issue for us to discuss the idea first.

## Finally

Thanks again for your interest in improving the project! You're taking action when most
people decide to sit and watch.
