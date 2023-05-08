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
      - uses: actions/checkout@v3
      - uses: psf/black@stable
```

We recommend the use of the `@stable` tag, but per version tags also exist if you prefer
that. Note that the action's version you select is independent of the version of _Black_
the action will use.

The version of _Black_ the action will use can be configured via `version`. This can be
any
[valid version specifier](https://packaging.python.org/en/latest/glossary/#term-Version-Specifier)
or just the version number if you want an exact version. The action defaults to the
latest release available on PyPI. Only versions available from PyPI are supported, so no
commit SHAs or branch names.

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

## Outputs

This action will output two variables for further processing of changes black has made
against `src` set.

### `is-formatted`

Defaults to `"false"`, set to `"true"` if black changed any files.

### `changed-files`

Defaults to `"0"`, set to string representation of integer value of how many files black
modified.

### Usage

One could use either of these output variables to further have conditional steps within
the same pipeline, like creating a pull request after black has done changes to the code
base.

```yaml
- uses: psf/black@stable
  with:
    options: "--verbose"
    src: "./src"
    id: "action_black"

- name: Create Pull Request
  if: steps.action_black.outputs.is-formatted == 'true'
  uses: peter-evans/create-pull-request@v3
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    title: "Format Python code with psf/black push"
    commit-message: ":art: Format Python code with psf/black"
    body: |
      There appear to be some python formatting errors in ${{ github.sha }}. This pull request
      uses the [psf/black](https://github.com/psf/black) formatter to fix these issues.
    base: ${{ github.head_ref }} # Creates pull request onto pull request or commit branch
```
