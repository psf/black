# Version control integration

Use [pre-commit](https://pre-commit.com/). Once you
[have it installed](https://pre-commit.com/#install), add this to the
`.pre-commit-config.yaml` in your repository:

```yaml
repos:
  # Using this mirror lets us use mypyc-compiled black, which is about 2x faster
  - repo: https://github.com/psf/black-pre-commit-mirror
    rev: 25.12.0
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
    rev: 25.12.0
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
 
 ## Using Black with pre-commit: how excludes work

When Black is used through pre-commit, pre-commit passes an explicit list of file paths
directly to Black. Because these paths are supplied on the command line, Black will format
them even if they match exclude or extend-exclude patterns from pyproject.toml. Black applies
those patterns only during its own file discovery step, which pre-commit bypasses.

### Recommended: use pre-commit’s own exclude

The most reliable way to prevent files from being formatted is to use pre-commit’s built-in
exclude, which ensures those files are never passed to Black:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: stable
    hooks:
      - id: black
        exclude: ^migrations/
```

### Excluding files in pyproject.toml

You can also configure exclusions inside pyproject.toml so that Black applies them when used
from the command line or other tools. However, these patterns will not stop pre-commit from
formatting files unless combined with --force-exclude, since pre-commit bypasses Black’s file
discovery:

```toml
[tool.black]
force_exclude = '''
/(
    migrations
  | build
  | dist
)/
'''
```

### Using --force-exclude when needed

--force-exclude tells Black to apply its exclude rules even when the file paths are given
explicitly (as pre-commit does). This can be useful when you want Black’s exclude patterns to
still apply, but it should be used as a fallback instead of the main approach:

```yaml
args: [ "--force-exclude=tests/" ]
```

