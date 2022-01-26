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
formatting don't need to be mentioned separately though. If the change is implemented
with the `--preview` flag, please include the change in the future style document
instead and write the changelog entry under a dedicated "Preview changes" heading.

### Docs Testing

If you make changes to docs, you can test they still build locally too.

```console
(.venv)$ pip install -r docs/requirements.txt
(.venv)$ pip install [-e] .[d]
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
