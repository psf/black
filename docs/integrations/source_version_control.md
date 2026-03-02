# Version control integration

Use [pre-commit](https://pre-commit.com/). Once you
[have it installed](https://pre-commit.com/#install), add this to the
`.pre-commit-config.yaml` in your repository:

```yaml
repos:
  # Using this mirror lets us use mypyc-compiled black, which is about 2x faster
  - repo: https://github.com/psf/black-pre-commit-mirror
    rev: 26.1.0
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
  - repo: https://github.com/psf/black-pre-commit-mirror
    rev: 26.1.0
    hooks:
      - id: black-jupyter
        language_version: python3.11
```

```{note}
The `black-jupyter` hook became available in version 21.8b0.
```

See the [Jupyter Notebooks guide](../guides/using_black_with_jupyter_notebooks.md) for
more details.

## Excluding files with pre-commit

When using pre-commit, there's an important distinction in how file exclusions work.
Pre-commit passes files directly to Black via the command line, rather than letting
Black discover files recursively. This means Black's `--exclude` option won't work as
expected because it only applies to files discovered during recursive directory
traversal.

To exclude files when using pre-commit, you have two options:

### Option 1: Use pre-commit's exclude (Recommended)

Configure exclusions directly in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black-pre-commit-mirror
    rev: 26.1.0
    hooks:
      - id: black
        exclude: ^migrations/|^generated/
```

This is the recommended approach because pre-commit filters files before passing them to
Black, avoiding unnecessary processing.

### Option 2: Use Black's force-exclude in pyproject.toml

Black's `force-exclude` configuration option excludes files even when they are passed
explicitly as command-line arguments (which is how pre-commit invokes Black). Simply add
the pattern to your `pyproject.toml`:

```toml
[tool.black]
force-exclude = '''
(
  ^migrations/
  | ^generated/
)
'''
```

Black automatically reads this configuration—no additional CLI arguments are needed in
your `.pre-commit-config.yaml`.

```{note}
The `force-exclude` option was added in version 20.8b0 specifically to support
workflows where files are passed directly via CLI, such as pre-commit hooks and
editor plugins.
```

[pre-commit-mutable-rev]:
  https://pre-commit.com/#using-the-latest-version-for-a-repository
