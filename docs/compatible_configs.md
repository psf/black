# _Black_ compatible configurations

_Black_ is a Python code formatter. Most of the changes that _Black_ make are harmless,
but a few do conflict against other tools. It is not uncommon to be using other tools
alongside _Black_ like linters and type checkers. Some of them need a bit of tweaking to
resolve the conflicts. Listed below are _Black_ compatible configurations for the
commonly used tools out there.

## isort

<details>
<summary>.isort.cfg</summary>

```cfg
[settings]
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
combine_as_imports = true
line_length = 88
```

</details>

<details>
<summary>setup.cfg</summary>

```cfg
[isort]
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
combine_as_imports = true
line_length = 88
```

</details>

<details>
<summary>pyproject.toml</summary>

```toml
[tool.isort]
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
combine_as_imports = true
line_length = 88
```

</details>

<details>
<summary>.editorconfig</summary>

```ini
[*.py]
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
combine_as_imports = true
line_length = 88
```

</details>

## flake8

<details>
<summary>.flake8</summary>

```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
```

</details>

<details>
<summary>setup.cfg</summary>

```cfg
[flake8]
max-line-length = 88
extend-ignore = E203, W503
```

</details>

<details>
<summary>tox.ini</summary>

```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
```

</details>

## pylint

<details>
<summary>pylintrc</summary>

```rc
[MESSAGES CONTROL]
disable = C0330, C0326

[format]
max-line-length = 88
```

</details>

<details>
<summary>setup.cfg</summary>

```cfg
[pylint]
max-line-length = 88

[pylint.messages_control]
disable = C0330, C0326
```

</details>

<details>
<summary>pyproject.toml</summary>

```toml
[tool.pylint.messages_control]
disable = "C0330, C0326"

[tool.pylint.format]
max-line-length = "88"
```

</details>
