# Using Pants

***Pants use in this repo is currently a proof-of-concept. It is not required for
contributing, so you can skip this page if not interested.***

[Pants](https://www.pantsbuild.org) is a build system with a strong focus on Python
support. Pants installs, configures and orchestrates many underlying standard tools,
including Pytest, Mypy, Flake8, Setuptools and many more, including, of course, _Black_
itself.

Pants uses static analysis to learn information about the structure and dependencies of
a codebase, and uses that data for fine-grained invalidation, hermetic execution,
caching and concurrency, to make builds fast and repeatable.

Pants has recently been introduced into this repo on an experimental basis, so that
Black contributors can try it out. It does not currently replace any of the
[established tools and processes](the_basics.md) for developing in this repo. Its use,
in this repo and in general, is supported by the Pants maintainers (who are
[happy to help](https://www.pantsbuild.org/docs/getting-help)), and not by other _Black_
maintainers.

## Installing Pants

The `./pants` runner script at the root of the repo will install or upgrade Pants as
needed. Multiple versions of Pants can coexist on a system, and the runner script
ensures that the appropriate version of Pants is used in a given repo.

Therefore this is enough to ensure a working installation of Pants at the appropriate
version:

```console
$ ./pants
```

## Cheat sheet

### Running tests

```console

# Run all tests on all supported Python versions.
$ ./pants test tests/::

# Run all tests on a specific set of Python versions.
$ ./pants test tests:tests-py38 tests:tests-py39

# Run a specific test on all supported Python versions.
$ ./pants test tests/test_format.py

# Run a specific test on a specific set of Python versions.
$ ./pants test tests/test_format.py:tests-py38 tests/test_format.py:tests-py39

# Pass Pytest args to a test.
$ ./pants test tests/test_format.py:tests-py38 -- -k test_empty

# Run only the tests that are affected by changes.
$ ./pants --changed-since=main --changed-dependees=transitive test

# See which test targets are available.
$ ./pants list tests:
```

### Building distributions

```console

# Building all distributions (native and pure Python) for all supported Python versions.
$ ./pants package :

# Building native wheels for specific Python versions.
$ ./pants package :dist-native@interpreter_constraints=py38 :dist-native@interpreter_constraints=py39

# Building the pure Python wheel and sdist.
$ ./pants package :dist-pure
```

### Linting

```console
# Run Flake8 and Black (in lint mode) on all relevant files.
$ ./pants lint ::

# Lint specific files.
$ ./pants lint src/black/brackets.py src/black/strings.py

# Lint only changed files.
$ ./pants --changed-since=main lint
```

Note that Flake8 will fail on `src/black/__init__.py` with the error
`C901 'main' is too complex (19)`, if run on Python 3.6. Pants may happen to choose that
interpreter if available on your system, since it is compatible with _Black_'s declared
interpreter constraints.

Pants is working on a change to support forcing a specific interpreter for Flake8. But
it may make also sense to update `.flake8` to `max-complexity = 19`, as that is in fact
the percieved complexity when computed on Python 3.6.

### Formatting

```console
# Run a published version of Black on all relevant files.
$ ./pants fmt ::

# Format specific files.
$ ./pants fmt src/black/brackets.py src/black/strings.py

# Format only changed files.
$ ./pants --changed-since=main fmt
```

### Running _Black_ from source on its own sources

```console
# Run _Black_ from source on specific files (expanded by the shell).
$ ./pants run src/black:main -- src/*.py tests/*.py *.py
```

Note that the args after `--` are passed sraight to _Black_, so Pants-specific notation
(e,g., `::`) does not work in that position.

TODO: Allow the `fmt` goal to run Black from sources instead of a published version.

### Typechecking

```console
# Run Mypy all relevant files.
$ ./pants check ::

# Check specific files.
$ ./pants check src/black/brackets.py src/black/strings.py

# Check only changed files.
$ ./pants --changed-since=main fmt
```

Note that some files currently fail typechecking via Pants, even though they succeed
with pre-commit. We believe that the failures are correct, and are a result of Pants
running Mypy with all the code's requirements present (as is recommended and expected by
Mypy), whereas the current pre-commit config runs Mypy in a virtualenv with only a
bespoke subset of the requirements present.

TODO: Reconcile this.

## The least you need to know

### The command line

A Pants invocation looks like this:

```console
$ ./pants [flags] <goals> <targets>
```

Goals are verbs such as "test", "check", and "lint". Targets are specifications of files
to act on.

You can see the available goals via `./pants help goals`, or
[online](https://www.pantsbuild.org/docs/reference-all-goals.

### Options

Any option can be set via the `pants.toml` config file, env var or cmd-line flag.

The option reference is available via `./pants help`, and online:

- [Global options](https://www.pantsbuild.org/docs/reference-global)
- [Subsystem options](https://www.pantsbuild.org/docs/reference-all-subsystems)

### BUILD files

Pants reads information about source code from metadata files named `BUILD`. These files
describe the structure and meaning of the code.

Pants usually infers dependencies via static analysis, but occasionally you may need to
manually specify a dependency in the appropriate BUILD file.

The BUILD file metadata reference is available via `./pants help targets`, and
[online](https://www.pantsbuild.org/docs/reference-all-targets).

### Lockfiles

For security and repeatability, Pants can generate and use lockfiles that pin versions
of all transitive requirements, verifying them against a SHA before use.

There are [lockfiles](../../lockfiles/default.lock) for the repo's requirements, and for the
requirements of the tools that Pants invokes, such as Pytest and Flake8.

To generate new lockfiles, typically because you've changed a `requirements.txt` file or
some relevant config, or you want to pick up the latest version on PyPI, run:

```
# Regenerate the repo's requirements lockfile.
$ ./pants generate-lockfiles --resolve=default

# Regenerate pytest's lockfile.
$ ./pants generate-lockfiles --resolve=pytest

# Regenerate all lockfiles.
$ ./pants generate-lockfiles
```

### The Pants daemon

Pants runs a daemon, pantsd, that keeps state memoized in RAM, for performance.

Log lines like these mean the daemon had to restart:

```
[INFO] Initializing scheduler...
[INFO] Scheduler initialized.
```

You can look at `.pants.d/pants.log` for details on why.

### Generating the _Black_ version string

_Black_ invokes [setuptools_scm](https://github.com/pypa/setuptools_scm) in [setup.py](../../setup.py)
to generate a gitignored \_black_version.py file on disk.

Pants, on the other hand, invokes setuptools_scm using its code generation mechanisms. A
\_black_version.py is generated and made available to any code that imports it, but it
is not written to disk.

To see what Pants generated, run

```console
./pants export-codegen src:vcs_version
```

## Not yet implemented

- Running fuzz testing
- Running diff-shades
- Generating docs

## Not yet supported

- Building Windows native wheels

Pants runs on the Windows Subsystem for Linux version 2 (WSL2), so it can be used for
development on a Windows system. But it does not yet work natively on Windows, and so
cannot build _Black_'s `win_amd64` wheels. This is a deficiency the Pants team is hoping
to resolve ASAP.
