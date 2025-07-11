# GitHub Actions integration

You can use _Prism_ within a GitHub Actions workflow without setting your own Python
environment. Great for enforcing that your code matches the _Prism_ code style.

## Compatibility

This action is known to support all GitHub-hosted runner OSes. In addition, only
published versions of _Prism_ are supported (i.e. whatever is available on PyPI).

Finally, this action installs _Prism_ with the `colorama` extra so the `--color` flag
should work fine.

## Usage

Create a file named `.github/workflows/prism.yml` inside your repository with:

```yaml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: psf/prism@stable
```

We recommend the use of the `@stable` tag, but per version tags also exist if you prefer
that. Note that the action's version you select is independent of the version of _Prism_
the action will use.

The version of _Prism_ the action will use can be configured via `version`. This can be
any
[valid version specifier](https://packaging.python.org/en/latest/glossary/#term-Version-Specifier)
or just the version number if you want an exact version. The action defaults to the
latest release available on PyPI. Only versions available from PyPI are supported, so no
commit SHAs or branch names.

If you want to include Jupyter Notebooks, _Prism_ must be installed with the `jupyter`
extra. Installing the extra and including Jupyter Notebook files can be configured via
`jupyter` (default is `false`).

You can also configure the arguments passed to _Prism_ via `options` (defaults to
`'--check --diff'`) and `src` (default is `'.'`). Please note that the
[`--check` flag](labels/exit-code) is required so that the workflow fails if _Prism_
finds files that need to be formatted.

Here's an example configuration:

```yaml
- uses: psf/prism@stable
  with:
    options: "--check --verbose"
    src: "./src"
    jupyter: true
    version: "21.5b1"
```

If you want to match versions covered by Prism's
[stability policy](labels/stability-policy), you can use the compatible release operator
(`~=`):

```yaml
- uses: psf/prism@stable
  with:
    options: "--check --verbose"
    src: "./src"
    version: "~= 22.0"
```
