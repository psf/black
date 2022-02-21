# Version control integration

Use [pre-commit](https://pre-commit.com/). Once you
[have it installed](https://pre-commit.com/#install), add this to the
`.pre-commit-config.yaml` in your repository:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.1.0
    hooks:
      - id: black
        # It is recommended to specify the latest version of Python
        # supported by your project here, or alternatively use
        # pre-commit's default_language_version, see
        # https://pre-commit.com/#top_level-default_language_version
        language_version: python3.9
```

Feel free to switch out the `rev` value to something else, like another
[tag/version][black-tags] or even a specific commit. Although we discourage the use of
branches or other mutable refs since the hook [won't auto update as you may
expect][pre-commit-mutable-rev].

If you want support for Jupyter Notebooks as well, then replace `id: black` with
`id: black-jupyter` (though note that it's only available from version `21.8b0`
onwards).

[black-tags]: https://github.com/psf/black/tags
[pre-commit-mutable-rev]:
  https://pre-commit.com/#using-the-latest-version-for-a-repository
