<!--
black documentation master file, created by
sphinx-quickstart on Fri Mar 23 10:53:30 2018.
-->

# The uncompromising code formatter

> “Any color you like.”

By using _Black_, you agree to cede control over minutiae of hand-formatting. In return,
_Black_ gives you speed, determinism, and freedom from `pycodestyle` nagging about
formatting. You will save time and mental energy for more important matters.

_Black_ makes code review faster by producing the smallest diffs possible. Blackened
code looks the same regardless of the project you're reading. Formatting becomes
transparent after a while and you can focus on the content instead.

Try it out now using the [Black Playground](https://black.vercel.app).

```{admonition} Note - Black is now stable!
*Black* is [successfully used](https://github.com/psf/black#used-by) by
many projects, small and big. *Black* has a comprehensive test suite, with efficient
parallel tests, our own auto formatting and parallel Continuous Integration runner.
Now that we have become stable, you should not expect large formatting to changes in
the future. Stylistic changes will mostly be responses to bug reports and support for new Python
syntax.

Also, as a safety measure which slows down processing, *Black* will check that the
reformatted code still produces a valid AST that is effectively equivalent to the
original (see the
[Pragmatism](./the_black_code_style/current_style.md#pragmatism)
section for details). If you're feeling confident, use `--fast`.
```

```{note}
{doc}`Black is licensed under the MIT license <license>`.
```

## Testimonials

**Mike Bayer**, author of [SQLAlchemy](https://www.sqlalchemy.org/):

> _I can't think of any single tool in my entire programming career that has given me a
> bigger productivity increase by its introduction. I can now do refactorings in about
> 1% of the keystrokes that it would have taken me previously when we had no way for
> code to format itself._

**Dusty Phillips**,
[writer](https://smile.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=dusty+phillips):

> _Black is opinionated so you don't have to be._

**Hynek Schlawack**, creator of [attrs](https://www.attrs.org/), core developer of
Twisted and CPython:

> _An auto-formatter that doesn't suck is all I want for Xmas!_

**Carl Meyer**, [Django](https://www.djangoproject.com/) core developer:

> _At least the name is good._

**Kenneth Reitz**, creator of [requests](http://python-requests.org/) and
[pipenv](https://docs.pipenv.org/):

> _This vastly improves the formatting of our code. Thanks a ton!_

## Show your style

Use the badge in your project's README.md:

```md
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
```

Using the badge in README.rst:

```rst
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
```

Looks like this:

```{image} https://img.shields.io/badge/code%20style-black-000000.svg
:target: https://github.com/psf/black
```

## Contents

```{toctree}
---
maxdepth: 3
includehidden:
---

the_black_code_style/index
```

```{toctree}
---
maxdepth: 3
includehidden:
caption: User Guide
---

getting_started
usage_and_configuration/index
integrations/index
guides/index
faq
```

```{toctree}
---
maxdepth: 2
includehidden:
caption: Development
---

contributing/index
change_log
authors
```

```{toctree}
---
hidden:
caption: Project Links
---

GitHub <https://github.com/psf/black>
PyPI <https://pypi.org/project/black>
Chat <https://discord.gg/RtVdv86PrH>
```

# Indices and tables

- {ref}`genindex`
- {ref}`search`
