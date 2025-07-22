# GitHub Actions integration

You can use _Black_ within a GitHub Actions workflow without setting your own Python
environment. Great for enforcing that your code matches the _Black_ code style.

## Compatibility

This action is known to support all GitHub-hosted runner OSes. In addition, only
published versions of _Black_ are supported (i.e. whatever is available on PyPI).

Finally, this action installs _Black_ with the `colorama` extra so the `--color` flag
should work fine.

## Usage

Create a file named `.github/workflows/black.yml` inside your repository with:

```yaml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: psf/black@stable
```

We recommend the use of the `@stable` tag, but per version tags also exist if you prefer
that. Note that the action's version you select is independent of the version of _Black_
the action will use.

The version of _Black_ the action will use can be configured via `version` or read from
the `pyproject.toml` file. `version` can be any
[valid version specifier](https://packaging.python.org/en/latest/glossary/#term-Version-Specifier)
or just the version number if you want an exact version. To read the version from the
`pyproject.toml` file instead, set `use_pyproject` to `true`. This will first look into
the `tool.black.required-version` field, then the `dependency-groups` table, then the
`project.dependencies` array and finally the `project.optional-dependencies` table. The
action defaults to the latest release available on PyPI. Only versions available from
PyPI are supported, so no commit SHAs or branch names.

If you want to include Jupyter Notebooks, _Black_ must be installed with the `jupyter`
extra. Installing the extra and including Jupyter Notebook files can be configured via
`jupyter` (default is `false`).

You can also configure the arguments passed to _Black_ via `options` (defaults to
`'--check --diff'`) and `src` (default is `'.'`). Please note that the
[`--check` flag](labels/exit-code) is required so that the workflow fails if _Black_
finds files that need to be formatted.

Here's an example configuration:

```yaml
- uses: psf/black@stable
  with:
    options: "--check --verbose"
    src: "./src"
    jupyter: true
    version: "21.5b1"
```

If you want to match versions covered by Black's
[stability policy](labels/stability-policy), you can use the compatible release operator
(`~=`):

```yaml
- uses: psf/black@stable
  with:
    options: "--check --verbose"
    src: "./src"
    version: "~= 22.0"
```

If you want to read the version from `pyproject.toml`, set `use_pyproject` to `true`.
Note that this requires Python >= 3.11, so using the setup-python action may be
required, for example:

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.13"
- uses: psf/black@stable
  with:
    options: "--check --verbose"
    src: "./src"
    use_pyproject: true
```
