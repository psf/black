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
      - uses: actions/checkout@v2
      - uses: psf/black@stable
```

We recommend the use of the `@stable` tag, but per version tags also exist if you prefer
that. Note that the action's version you select is independent of the version of _Black_
the action will use.

The version of _Black_ the action will use can be configured via `version`. The action
defaults to the latest release available on PyPI. Only versions available from PyPI are
supported, so no commit SHAs or branch names.

You can also configure the arguments passed to _Black_ via `options` (defaults to
`'--check --diff'`) and `src` (default is `'.'`)

Here's an example configuration:

```yaml
- uses: psf/black@stable
  with:
    options: "--check --verbose"
    src: "./src"
    version: "21.5b1"
```
