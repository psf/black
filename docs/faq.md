# Frequently Asked Questions

The most common questions and issues users face are aggregated to this FAQ.

```{contents}
:local:
:backlinks: none
:class: this-will-duplicate-information-and-it-is-still-useful-here
```

## Why spaces? I prefer tabs

PEP 8 recommends spaces over tabs, and they are used by most of the Python community.
_Black_ provides no options to configure the indentation style, and requests for such
options will not be considered.

However, we recognise that using tabs is an accessibility issue as well. While the
option will never be added to _Black_, visually impaired developers may find conversion
tools such as `expand/unexpand` (for Linux) useful when contributing to Python projects.
A workflow might consist of e.g. setting up appropriate pre-commit and post-merge git
hooks, and scripting `unexpand` to run after applying _Black_.

## Does Black have an API?

Not yet. _Black_ is fundamentally a command line tool. Many
[integrations](/integrations/index.md) are provided, but a Python interface is not one
of them. A simple API is being [planned](https://github.com/psf/black/issues/779)
though.

## Is Black safe to use?

Yes. _Black_ is strictly about formatting, nothing else. Black strives to ensure that
after formatting the AST is
[checked](the_black_code_style/current_style.md#ast-before-and-after-formatting) with
limited special cases where the code is allowed to differ. If issues are found, an error
is raised and the file is left untouched. Magical comments that influence linters and
other tools, such as `# noqa`, may be moved by _Black_. See below for more details.

## How stable is Black's style?

Stable. _Black_ aims to enforce one style and one style only, with some room for
pragmatism. See [The Black Code Style](the_black_code_style/index.md) for more details.

Starting in 2022, the formatting output is stable for the releases made in the same year
(other than unintentional bugs). At the beginning of every year, the first release will
make changes to the stable style. It is possible to opt in to the latest formatting
styles using the `--preview` flag.

## Why is my file not formatted?

Most likely because it is ignored in `.gitignore` or excluded with configuration. See
[file collection and discovery](usage_and_configuration/file_collection_and_discovery.md)
for details.

## Why is my Jupyter Notebook cell not formatted?

_Black_ is timid about formatting Jupyter Notebooks. Cells containing any of the
following will not be formatted:

- automagics (e.g. `pip install black`)
- non-Python cell magics (e.g. `%%writefile`)
- multiline magics
- code which `IPython`'s `TransformerManager` would transform magics into
- invalid syntax

See
[Using _Black_ with Jupyter Notebooks](guides/using_black_with_jupyter_notebooks.md#cells-that-black-will-skip)
for details.

## Why does Flake8 report warnings?

Some of Flake8's rules conflict with Black's style. We recommend disabling these rules.
See [Using _Black_ with other tools](labels/why-pycodestyle-warnings).

## Which Python versions does Black support?

_Black_ generally supports all Python versions supported by CPython (see
[the Python devguide](https://devguide.python.org/versions/) for current information).
We promise to support at least all Python versions that have not reached their end of
life. This is the case for both running _Black_ and formatting code.

Support for formatting Python 2 code was removed in version 22.0. While we've made no
plans to stop supporting older Python 3 minor versions immediately, their support might
also be removed some time in the future without a deprecation period.

`await`/`async` as soft keywords/indentifiers are no longer supported as of 25.9.0.

Runtime support for 3.6 was removed in version 22.10.0, for 3.7 in version 23.7.0, for
3.8 in version 24.10.0, and for 3.9 in version 25.12.0.

## Why does my linter or typechecker complain after I format my code?

Some linters and other tools use magical comments (e.g., `# noqa`, `# type: ignore`) to
influence their behavior. While Black does its best to recognize such comments and leave
them in the right place, this detection is not and cannot be perfect. Therefore, you'll
sometimes have to manually move these comments to the right place after you format your
codebase with _Black_.

## Can I run Black with PyPy?

Yes, there is support for PyPy 3.8 and higher.

## Why does Black not detect syntax errors in my code?

_Black_ is an autoformatter, not a Python linter or interpreter. Detecting all syntax
errors is not a goal. It can format all code accepted by CPython (if you find an example
where that doesn't hold, please report a bug!), but it may also format some code that
CPython doesn't accept.

(labels/mypyc-support)=

## What is `compiled: yes/no` all about in the version output?

While _Black_ is indeed a pure Python project, we use [mypyc] to compile _Black_ into a
C Python extension, usually doubling performance. These compiled wheels are available
for 64-bit versions of Windows (both AMD and ARM), Linux (via the manylinux standard),
and macOS across all supported CPython versions.

Platforms including musl-based and/or ARM Linux distributions are currently **not**
supported. These platforms will fall back to the slower pure Python wheel available on
PyPI.

If you are experiencing exceptionally weird issues or even segfaults, you can try
passing `--no-binary black` to your pip install invocation. This flag excludes all
wheels (including the pure Python wheel), so this command will use the [sdist].

[mypyc]: https://mypyc.readthedocs.io/en/latest/
[sdist]:
  https://packaging.python.org/en/latest/glossary/#term-Source-Distribution-or-sdist

## Why are emoji not displaying correctly on Windows?

When using Windows, the emoji in _Black_'s output may not display correctly. This is not
fixable from _Black_'s end.

Instead, run your chosen command line/shell through [Windows Terminal], which will
properly handle rendering the emoji.

[Windows Terminal]: https://github.com/microsoft/terminal
