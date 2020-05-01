# _Black_ compatible configurations

Most of the changes that _Black_ make are harmless, but a few do conflict against other
tools. It is not uncommon to be using other tools alongside _Black_ like linters and
type checkers. Some of them need a bit of tweaking to resolve the conflicts. Listed
below are _Black_ compatible configurations for the commonly used tools out there with
their explanations.

## isort

[isort](https://pypi.org/p/isort/) helps to sort and format imports in your Python code.
_Black_ also formats imports, but in a different way from isort's defaults which leads
to conflicting changes.

_Black_ wraps imports that surpass `line-length` by moving identifiers into their own
indented line. If that still doesn't fit the bill, it will put all of them in seperate
lines and put a trailing comma. A more detailed explanation of this behaviour can be
[found here](https://github.com/psf/black#how-black-wraps-lines).

isort should be configured to match _Black_'s import formatting style by these options:

- `multi_line_output = 3`
- `include_trailing_comma = true`
- `force_grid_wrap = 0`
- `combine_as_imports = true`

isort should be configured to wrap imports when they surpass _Black_'s default limit of
88 characters via `line_length = 88`.

### Formats

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

[flake8](https://pypi.org/p/flake8/) is a code linter. It warns you of syntax errors,
possible bugs, stylistic errors, etc. For the most part, flake8 follows
[PEP 8](https://www.python.org/dev/peps/pep-0008/) when warning about stylistic errors.
Except, there are a few deviations that cause incompatiblities with _Black_.

When breaking a line, _Black_ will break it before a binary operator. This is compliant
with PEP 8, but this behaviour will cause flake8 to raise
`W503 line break before binary operator` warnings.

In some cases, as determined by PEP 8, _Black_ will enforce an equal amount of
whitespace around slice operators. Due to this, flake8 will raise
`E203 whitespace before ':'` warnings.

Since both of these warnings are not PEP 8 compliant, flake8 should be configured to
ignore these warnings via `extend-ignore = E203, W503`.

Also, as like with isort, flake8 should be configured to allow lines up to the length
limit of `88`, _Black_'s default. This explains `max-line-length = 88`.

### Formats

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

[pylint](https://pypi.org/p/pylint/) is also a code linter like flake8. It has the same
checks as flake8 and more. In particular, it has more formatting checks regarding style
conventions like variable naming. With so many checks, pylint is bound to have some
mixed feelings about _Black_'s formatting style.

When _Black_ is folding very long expressions, the closing brackets will be dedented.
The explanation behind this can be
[found here](https://github.com/psf/black#how-black-wraps-lines).

```py3
ImportantClass.important_method(
    exc, limit, lookup_lines, capture_locals, callback
)
```

Although, while this style is PEP 8 compliant, pylint will raise
`C0330: Wrong hanging indentation before block (add 4 spaces)` warnings. Since _Black_
isn't configurable on this style, pylint should be told to ignore these warnings via
`disable = C0330`.

Also, since _Black_ deals with whitespace around operators and brackets, pylint's
warning `C0326: Bad whitespace` should be disabled using `disable = C0326`.

Plus, as usual, pylint should be configured to complain about lines that surpass `88`
characters via `max-line-length == 88` so pylint will respect _Black_'s default.

### Formats

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
