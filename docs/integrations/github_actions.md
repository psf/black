# GitHub Actions integration

You can use _Black_ within a GitHub Actions workflow without setting your own Python
environment. Great for enforcing that your code matches the _Black_ code style.

## Setting it up

Create a file named `.github/workflows/black.yml` inside your repository with:

```yaml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - uses: psf/black@stable
        with:
          black_args: ". --check"
```

## Inputs

### `black_args`

**optional**: Black input arguments. Defaults to `. --check --diff`.
