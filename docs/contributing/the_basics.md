# The basics

An overview on contributing to the _Black_ project.

## Technicalities

Development on the latest version of Python is preferred. As of this writing it's 3.9.
You can use any operating system.

Most development tasks are automated by [nox][nox] which automatically creates virtual
environments and running the right commands. You'll most likely run the test suite,
build docs, etc. using nox. Often, you can run `python -m pip install nox` to install
and use it.

```{tip}
If you're on Linux or MacOS you might want to use [pipx][pipx] to install nox (and
optionally pre-commit) to avoid interfering with the system Python installation.

Alternatively install them into the virtual environment you'll be setting up below.
```

### Running black from source tree

To run the `black` executable from your source tree during development, install _Black_
locally using editable installation (inside a virtual environment). You can then invoke
your local source tree _Black_ normally.

**Linux / MacOS**

```console
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv)$ pip install -e .[d,jupyter]
```

**Windows**

```console
$ py -m venv .venv
$ .venv\Scripts\activate
(.venv)$ python -m pip install -e .[d,jupyter]
```

### Running linters

_Black_ uses [pre-commit][pre-commit] to manage linting. It has been configured with a
list of _pre-commit hooks_ that each check a certain aspect of the codebase.

```console
$ nox -s lint
```

You can also setup pre-commit to automatically run before committing. First, install
pre-commit similarly to nox and install the Git pre commit hook:

```console
$ python -m pip install pre-commit
$ pre-commit install
```

### Running tests

Before opening a pull request that involves code, please run the test suite to verify
the changes didn't break anything.

```console
$ nox -s tests-3.9
```

The example above runs tests against Python 3.9. You can also use other versions like
`3.7` and `pypy3`. If you don't specify a Python version, nox will look for Python
installations for all the versions _Black_ supports and run the suite for each!

By default, the test suite is ran with coverage and parallelization enabled, but you can
disable them if they're causing you trouble:

```console
# to disable parallelization
$ nox -s tests-3.9 -- --no-xdist
# to disable coverage
$ nox -s tests-3.9 -- --no-cov
# to disable both
$ nox -s tests-3.9 -- --no-cov --no-xdist
```

If you need to run the test suite manually, install the test dependencies in the virtual
environment you've [previously set up](#running-black-from-source-tree) and then run
pytest:

**Linux / MacOS**

```console
(.venv)$ pip install -r tests/requirements.txt
(.venv)$ pytest
```

**Windows**

```console
(.venv)$ python -m pip install -r tests\requirements.txt
(.venv)$ pytest
```

### Building documentation

If you make changes to docs, you can test they still build locally too.

```console
$ nox -s docs
```

If you are making many changes to docs, you may find it helpful to use the `docs-live`
session. Each time you make a change to the docs they're rebuilt and the browser tab
reloads.

```console
$ nox -s docs-live
```

## Style changes

If a change would affect the advertised code style, please modify the documentation (The
_Black_ code style) to reflect that change. Patches that fix unintended bugs in
formatting don't need to be mentioned separately though. If the change is implemented
with the `--preview` flag, please include the change in
{doc}`/the_black_code_style/future_style` instead and write the changelog entry under a
dedicated "Preview changes" heading.

## Changelog requirement

_Black_ has CI that will check for an entry corresponding to your PR in `CHANGES.md`. If
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

## Hygiene

If you're fixing a bug, add a test. Run it first to confirm it fails, then fix the bug,
run it again to confirm it's really fixed.

If adding a new feature, add a test. In fact, always add a test. But wait, before adding
any large feature, first open an issue for us to discuss the idea first.

## Finally

Thanks again for your interest in improving the project! You're taking action when most
people decide to sit and watch. If you ever need help feel free to ask on the relevant
issue or chat with us in the [Python Discord server](https://discord.gg/RtVdv86PrH).

[nox]: https://nox.thea.codes/en/stable/
[pipx]: https://pypa.github.io/pipx/
[pre-commit]: https://pre-commit.com/
