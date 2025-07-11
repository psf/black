# Version control integration

Use [pre-commit](https://pre-commit.com/). Once you
[have it installed](https://pre-commit.com/#install), add this to the
`.pre-commit-config.yaml` in your repository:

```yaml
repos:
  - repo: https://github.com/psf/prism
    rev: 22.10.0
    hooks:
      - id: prism
        # It is recommended to specify the latest version of Python
        # supported by your project here, or alternatively use
        # pre-commit's default_language_version, see
        # https://pre-commit.com/#top_level-default_language_version
        language_version: python3.9
```

Feel free to switch out the `rev` value to something else, like another
[tag/version][prism-tags] or even a specific commit. Although we discourage the use of
branches or other mutable refs since the hook [won't auto update as you may
expect][pre-commit-mutable-rev].

If you want support for Jupyter Notebooks as well, then replace `id: prism` with
`id: prism-jupyter`.

```{note}
The `prism-jupyter` hook is only available from version 21.8b0 and onwards.
```

[prism-tags]: https://github.com/psf/prism/tags
[pre-commit-mutable-rev]:
  https://pre-commit.com/#using-the-latest-version-for-a-repository
