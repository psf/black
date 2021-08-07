# Version control integration

Use [pre-commit](https://pre-commit.com/). Once you
[have it installed](https://pre-commit.com/#install), add this to the
`.pre-commit-config.yaml` in your repository:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 21.7b0 # Replace by any tag/version: https://github.com/psf/black/tags
    hooks:
      - id: black
        language_version: python3 # Should be a command that runs python3.6+
```

If you want support for Jupyter Notebooks as well, then replace `id: black` with
`id: black-jupyter` (though note that it's only available from version `21.8b0`
onwards).
