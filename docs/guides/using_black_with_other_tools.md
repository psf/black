# Using _Black_ with other tools

## Black compatible configurations

All of Black's changes are harmless (or at least, they should be), but a few do conflict
against other tools. It is not uncommon to be using other tools alongside _Black_ like
linters and type checkers. Some of them need a bit of tweaking to resolve the conflicts.
Listed below are _Black_ compatible configurations in various formats for the common
tools out there.

**Please note** that _Black_ only supports the TOML file format for its configuration
(e.g. `pyproject.toml`). The provided examples are to only configure their corresponding
tools, using **their** supported file formats.

Compatible configuration files can be
[found here](https://github.com/psf/black/blob/main/docs/compatible_configs/).

### isort

[isort](https://pypi.org/p/isort/) helps to sort and format imports in your Python code.
_Black_ also formats imports, but in a different way from isort's defaults which leads
to conflicting changes.

#### Profile

Since version 5.0.0, isort supports
[profiles](https://pycqa.github.io/isort/docs/configuration/profiles.html) to allow easy
interoperability with common code styles. You can set the black profile in any of the
[config files](https://pycqa.github.io/isort/docs/configuration/config_files.html)
supported by isort. Below, an example for `pyproject.toml`:

```toml
[tool.isort]
profile = "black"
```

#### Custom Configuration

If you're using an isort version that is older than 5.0.0 or you have some custom
configuration for _Black_, you can tweak your isort configuration to make it compatible
with _Black_. Below, an example for `.isort.cfg`:

```
multi_line_output = 3
include_trailing_comma = True
force_grid_wrap = 0
use_parentheses = True
ensure_newline_before_comments = True
line_length = 88
```

#### Why those options above?

_Black_ wraps imports that surpass `line-length` by moving identifiers into their own
indented line. If that still doesn't fit the bill, it will put all of them in separate
lines and put a trailing comma. A more detailed explanation of this behaviour can be
[found here](../the_black_code_style/current_style.md#how-black-wraps-lines).

isort's default mode of wrapping imports that extend past the `line_length` limit is
"Grid".

```py3
from third_party import (lib1, lib2, lib3,
                         lib4, lib5, ...)
```

This style is incompatible with _Black_, but isort can be configured to use a different
wrapping mode called "Vertical Hanging Indent" which looks like this:

```py3
from third_party import (
    lib1,
    lib2,
    lib3,
    lib4,
)
```

This style is _Black_ compatible and can be achieved by `multi-line-output = 3`. Also,
as mentioned above, when wrapping long imports _Black_ puts a trailing comma and uses
parentheses. isort should follow the same behaviour and passing the options
`include_trailing_comma = True` and `use_parentheses = True` configures that.

The option `force_grid_wrap = 0` is just to tell isort to only wrap imports that surpass
the `line_length` limit.

Finally, isort should be told to wrap imports when they surpass _Black_'s default limit
of 88 characters via `line_length = 88` as well as
`ensure_newline_before_comments = True` to ensure spacing import sections with comments
works the same as with _Black_.

**Please note** `ensure_newline_before_comments = True` only works since isort >= 5 but
does not break older versions so you can keep it if you are running previous versions.

#### Formats

<details>
<summary>.isort.cfg</summary>

```ini
[settings]
profile = black
```

</details>

<details>
<summary>setup.cfg</summary>

```ini
[isort]
profile = black
```

</details>

<details>
<summary>pyproject.toml</summary>

```toml
[tool.isort]
profile = 'black'
```

</details>

<details>
<summary>.editorconfig</summary>

```ini
[*.py]
profile = black
```

</details>

### Flake8

[Flake8](https://pypi.org/p/flake8/) is a code linter. It warns you of syntax errors,
possible bugs, stylistic errors, etc. For the most part, Flake8 follows
[PEP 8](https://www.python.org/dev/peps/pep-0008/) when warning about stylistic errors.
There are a few deviations that cause incompatibilities with _Black_.

#### Configuration

```
max-line-length = 88
extend-ignore = E203
```

#### Why those options above?

In some cases, as determined by PEP 8, _Black_ will enforce an equal amount of
whitespace around slice operators. Due to this, Flake8 will raise
`E203 whitespace before ':'` warnings. Since this warning is not PEP 8 compliant, Flake8
should be configured to ignore it via `extend-ignore = E203`.

When breaking a line, _Black_ will break it before a binary operator. This is compliant
with PEP 8 as of
[April 2016](https://github.com/python/peps/commit/c59c4376ad233a62ca4b3a6060c81368bd21e85b#diff-64ec08cc46db7540f18f2af46037f599).
There's a disabled-by-default warning in Flake8 which goes against this PEP 8
recommendation called `W503 line break before binary operator`. It should not be enabled
in your configuration.

Also, as like with isort, flake8 should be configured to allow lines up to the length
limit of `88`, _Black_'s default. This explains `max-line-length = 88`.

#### Formats

<details>
<summary>.flake8</summary>

```ini
[flake8]
max-line-length = 88
extend-ignore = E203
```

</details>

<details>
<summary>setup.cfg</summary>

```ini
[flake8]
max-line-length = 88
extend-ignore = E203
```

</details>

<details>
<summary>tox.ini</summary>

```ini
[flake8]
max-line-length = 88
extend-ignore = E203
```

</details>

### Pylint

[Pylint](https://pypi.org/p/pylint/) is also a code linter like Flake8. It has the same
checks as flake8 and more. In particular, it has more formatting checks regarding style
conventions like variable naming. With so many checks, Pylint is bound to have some
mixed feelings about _Black_'s formatting style.

#### Configuration

```
disable = C0330, C0326
max-line-length = 88
```

#### Why those options above?

When _Black_ is folding very long expressions, the closing brackets will
[be dedented](../the_black_code_style/current_style.md#how-black-wraps-lines).

```py3
ImportantClass.important_method(
    exc, limit, lookup_lines, capture_locals, callback
)
```

Although this style is PEP 8 compliant, Pylint will raise
`C0330: Wrong hanging indentation before block (add 4 spaces)` warnings. Since _Black_
isn't configurable on this style, Pylint should be told to ignore these warnings via
`disable = C0330`.

Also, since _Black_ deals with whitespace around operators and brackets, Pylint's
warning `C0326: Bad whitespace` should be disabled using `disable = C0326`.

And as usual, Pylint should be configured to only complain about lines that surpass `88`
characters via `max-line-length = 88`.

#### Formats

<details>
<summary>pylintrc</summary>

```ini
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
