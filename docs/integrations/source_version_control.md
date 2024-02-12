# Version control integration

Use [pre-commit](https://pre-commit.com/). Once you
[have it installed](https://pre-commit.com/#install), add this to the
`.pre-commit-config.yaml` in your repository:

```yaml
repos:
  # Using this mirror lets us use mypyc-compiled black, which is about 2x faster
  - repo: https://github.com/psf/black-pre-commit-mirror
    rev: 24.1.1
    hooks:
      - id: black
        # It is recommended to specify the latest version of Python
        # supported by your project here, or alternatively use
        # pre-commit's default_language_version, see
        # https://pre-commit.com/#top_level-default_language_version
        language_version: python3.11
```

Feel free to switch out the `rev` value to a different version of Black.

Note if you'd like to use a specific commit in `rev`, you'll need to swap the repo
specified from the mirror to https://github.com/psf/black. We discourage the use of
branches or other mutable refs since the hook [won't auto update as you may
expect][pre-commit-mutable-rev].

## Jupyter Notebooks

There is an alternate hook `black-jupyter` that expands the targets of `black` to
include Jupyter Notebooks. To use this hook, simply replace the hook's `id: black` with
`id: black-jupyter` in the `.pre-commit-config.yaml`:

```yaml
repos:
  # Using this mirror lets us use mypyc-compiled black, which is about 2x faster
  - repo: https://github.com/psf/black-pre-commit-mirror
    rev: 24.1.1
    hooks:
      - id: black-jupyter
        # It is recommended to specify the latest version of Python
        # supported by your project here, or alternatively use
        # pre-commit's default_language_version, see
        # https://pre-commit.com/#top_level-default_language_version
        language_version: python3.11
```

```{note}
The `black-jupyter` hook became available in version 21.8b0.
```

[pre-commit-mutable-rev]:
  https://pre-commit.com/#using-the-latest-version-for-a-repository
