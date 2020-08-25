![Black Logo](https://raw.githubusercontent.com/psf/black/master/docs/_static/logo2-readme.png)

<h2 align="center">The Uncompromising Code Formatter</h2>

<p align="center">
<a href="https://travis-ci.com/psf/black"><img alt="Build Status" src="https://travis-ci.com/psf/black.svg?branch=master"></a>
<a href="https://github.com/psf/black/actions"><img alt="Actions Status" src="https://github.com/psf/black/workflows/Test/badge.svg"></a>
<a href="https://github.com/psf/black/actions"><img alt="Actions Status" src="https://github.com/psf/black/workflows/Primer/badge.svg"></a>
<a href="https://black.readthedocs.io/en/stable/?badge=stable"><img alt="Documentation Status" src="https://readthedocs.org/projects/black/badge/?version=stable"></a>
<a href="https://coveralls.io/github/psf/black?branch=master"><img alt="Coverage Status" src="https://coveralls.io/repos/github/psf/black/badge.svg?branch=master"></a>
<a href="https://github.com/psf/black/blob/master/LICENSE"><img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg"></a>
<a href="https://pypi.org/project/black/"><img alt="PyPI" src="https://img.shields.io/pypi/v/black"></a>
<a href="https://pepy.tech/project/black"><img alt="Downloads" src="https://pepy.tech/badge/black"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

> “Any color you like.”

_Black_ is the uncompromising Python code formatter. By using it, you agree to cede
control over minutiae of hand-formatting. In return, _Black_ gives you speed,
determinism, and freedom from `pycodestyle` nagging about formatting. You will save time
and mental energy for more important matters.

Blackened code looks the same regardless of the project you're reading. Formatting
becomes transparent after a while and you can focus on the content instead.

_Black_ makes code review faster by producing the smallest diffs possible.

Try it out now using the [Black Playground](https://black.now.sh). Watch the
[PyCon 2019 talk](https://youtu.be/esZLCuWs_2Y) to learn more.

---

_Contents:_ **[Installation and usage](#installation-and-usage)** |
**[Code style](#the-black-code-style)** | **[Pragmatism](#pragmatism)** |
**[pyproject.toml](#pyprojecttoml)** | **[Editor integration](#editor-integration)** |
**[blackd](#blackd)** | **[black-primer](#black-primer)** |
**[Version control integration](#version-control-integration)** |
**[GitHub Actions](#github-actions)** |
**[Ignoring unmodified files](#ignoring-unmodified-files)** | **[Used by](#used-by)** |
**[Testimonials](#testimonials)** | **[Show your style](#show-your-style)** |
**[Contributing](#contributing-to-black)** | **[Change log](#change-log)** |
**[Authors](#authors)**

---

## Installation and usage

### Installation

_Black_ can be installed by running `pip install black`. It requires Python 3.6.0+ to
run but you can reformat Python 2 code with it, too.

#### Install from GitHub

If you can't wait for the latest _hotness_ and want to install from GitHub, use:

`pip install git+git://github.com/psf/black`

### Usage

To get started right away with sensible defaults:

```sh
black {source_file_or_directory}
```

You can run _Black_ as a package if running it as a script doesn't work:

```sh
python -m black {source_file_or_directory}
```

### Command line options

_Black_ doesn't provide many options. You can list them by running `black --help`:

```text
Usage: black [OPTIONS] [SRC]...

  The uncompromising code formatter.

Options:
  -c, --code TEXT                 Format the code passed in as a string.
  -l, --line-length INTEGER       How many characters per line to allow.
                                  [default: 88]

  -t, --target-version [py27|py33|py34|py35|py36|py37|py38]
                                  Python versions that should be supported by
                                  Black's output. [default: per-file auto-
                                  detection]

  --pyi                           Format all input files like typing stubs
                                  regardless of file extension (useful when
                                  piping source on standard input).

  -S, --skip-string-normalization
                                  Don't normalize string quotes or prefixes.
  --check                         Don't write the files back, just return the
                                  status.  Return code 0 means nothing would
                                  change.  Return code 1 means some files
                                  would be reformatted. Return code 123 means
                                  there was an internal error.

  --diff                          Don't write the files back, just output a
                                  diff for each file on stdout.

  --color / --no-color            Show colored diff. Only applies when
                                  `--diff` is given.

  --fast / --safe                 If --fast given, skip temporary sanity
                                  checks. [default: --safe]

  --include TEXT                  A regular expression that matches files and
                                  directories that should be included on
                                  recursive searches.  An empty value means
                                  all files are included regardless of the
                                  name.  Use forward slashes for directories
                                  on all platforms (Windows, too).  Exclusions
                                  are calculated first, inclusions later.
                                  [default: \.pyi?$]

  --exclude TEXT                  A regular expression that matches files and
                                  directories that should be excluded on
                                  recursive searches.  An empty value means no
                                  paths are excluded. Use forward slashes for
                                  directories on all platforms (Windows, too).
                                  Exclusions are calculated first, inclusions
                                  later.  [default: /(\.eggs|\.git|\.hg|\.mypy
                                  _cache|\.nox|\.tox|\.venv|\.svn|_build|buck-
                                  out|build|dist)/]

  --force-exclude TEXT            Like --exclude, but files and directories
                                  matching this regex will be excluded even
                                  when they are passed explicitly as arguments

  -q, --quiet                     Don't emit non-error messages to stderr.
                                  Errors are still emitted; silence those with
                                  2>/dev/null.

  -v, --verbose                   Also emit messages to stderr about files
                                  that were not changed or were ignored due to
                                  --exclude=.

  --version                       Show the version and exit.
  --config FILE                   Read configuration from FILE path.
  -h, --help                      Show this message and exit.
```

_Black_ is a well-behaved Unix-style command-line tool:

- it does nothing if no sources are passed to it;
- it will read from standard input and write to standard output if `-` is used as the
  filename;
- it only outputs messages to users on standard error;
- exits with code 0 unless an internal error occurred (or `--check` was used).

### Using _Black_ with other tools

While _Black_ enforces formatting that conforms to PEP 8, other tools may raise warnings
about _Black_'s changes or will overwrite _Black_'s changes. A good example of this is
[isort](https://pypi.org/p/isort). Since _Black_ is barely configurable, these tools
should be configured to neither warn about nor overwrite _Black_'s changes.

Actual details on _Black_ compatible configurations for various tools can be found in
[compatible_configs](https://github.com/psf/black/blob/master/docs/compatible_configs.md).

### Migrating your code style without ruining git blame

A long-standing argument against moving to automated code formatters like _Black_ is
that the migration will clutter up the output of `git blame`. This was a valid argument,
but since Git version 2.23, Git natively supports
[ignoring revisions in blame](https://git-scm.com/docs/git-blame#Documentation/git-blame.txt---ignore-revltrevgt)
with the `--ignore-rev` option. You can also pass a file listing the revisions to ignore
using the `--ignore-revs-file` option. The changes made by the revision will be ignored
when assigning blame. Lines modified by an ignored revision will be blamed on the
previous revision that modified those lines.

So when migrating your project's code style to _Black_, reformat everything and commit
the changes (preferably in one massive commit). Then put the full 40 characters commit
identifier(s) into a file.

```
# Migrate code style to Black
5b4ab991dede475d393e9d69ec388fd6bd949699
```

Afterwards, you can pass that file to `git blame` and see clean and meaningful blame
information.

```console
$ git blame important.py --ignore-revs-file .git-blame-ignore-revs
7a1ae265 (John Smith 2019-04-15 15:55:13 -0400 1) def very_important_function(text, file):
abdfd8b0 (Alice Doe  2019-09-23 11:39:32 -0400 2)     text = text.lstrip()
7a1ae265 (John Smith 2019-04-15 15:55:13 -0400 3)     with open(file, "r+") as f:
7a1ae265 (John Smith 2019-04-15 15:55:13 -0400 4)         f.write(formatted)
```

You can even configure `git` to automatically ignore revisions listed in a file on every
call to `git blame`.

```console
$ git config blame.ignoreRevsFile .git-blame-ignore-revs
```

**The one caveat is that GitHub and GitLab do not yet support ignoring revisions using
their native UI of blame.** So blame information will be cluttered with a reformatting
commit on those platforms. (If you'd like this feature, there's an open issue for
[GitLab](https://gitlab.com/gitlab-org/gitlab/-/issues/31423) and please let GitHub
know!)

### NOTE: This is a beta product

_Black_ is already [successfully used](#used-by) by many projects, small and big. It
also sports a decent test suite. However, it is still very new. Things will probably be
wonky for a while. This is made explicit by the "Beta" trove classifier, as well as by
the "b" in the version number. What this means for you is that **until the formatter
becomes stable, you should expect some formatting to change in the future**. That being
said, no drastic stylistic changes are planned, mostly responses to bug reports.

Also, as a temporary safety measure, _Black_ will check that the reformatted code still
produces a valid AST that is equivalent to the original. This slows it down. If you're
feeling confident, use `--fast`.

## The _Black_ code style

_Black_ is a PEP 8 compliant opinionated formatter. _Black_ reformats entire files in
place. It is not configurable. It doesn't take previous formatting into account. Your
main option of configuring _Black_ is that it doesn't reformat blocks that start with
`# fmt: off` and end with `# fmt: on`. `# fmt: on/off` have to be on the same level of
indentation. To learn more about _Black_'s opinions, to go
[the_black_code_style](https://github.com/psf/black/blob/master/docs/the_black_code_style.md).

Please refer to this document before submitting an issue. What seems like a bug might be
intended behaviour.

## Pragmatism

Early versions of _Black_ used to be absolutist in some respects. They took after its
initial author. This was fine at the time as it made the implementation simpler and
there were not many users anyway. Not many edge cases were reported. As a mature tool,
_Black_ does make some exceptions to rules it otherwise holds. This
[section](https://github.com/psf/black/blob/master/docs/the_black_code_style.md#pragmatism)
of `the_black_code_style` describes what those exceptions are and why this is the case.

Please refer to this document before submitting an issue just like with the document
above. What seems like a bug might be intended behaviour.

## pyproject.toml

_Black_ is able to read project-specific default values for its command line options
from a `pyproject.toml` file. This is especially useful for specifying custom
`--include` and `--exclude` patterns for your project.

**Pro-tip**: If you're asking yourself "Do I need to configure anything?" the answer is
"No". _Black_ is all about sensible defaults.

### What on Earth is a `pyproject.toml` file?

[PEP 518](https://www.python.org/dev/peps/pep-0518/) defines `pyproject.toml` as a
configuration file to store build system requirements for Python projects. With the help
of tools like [Poetry](https://python-poetry.org/) or
[Flit](https://flit.readthedocs.io/en/latest/) it can fully replace the need for
`setup.py` and `setup.cfg` files.

### Where _Black_ looks for the file

By default _Black_ looks for `pyproject.toml` starting from the common base directory of
all files and directories passed on the command line. If it's not there, it looks in
parent directories. It stops looking when it finds the file, or a `.git` directory, or a
`.hg` directory, or the root of the file system, whichever comes first.

If you're formatting standard input, _Black_ will look for configuration starting from
the current working directory.

You can also explicitly specify the path to a particular file that you want with
`--config`. In this situation _Black_ will not look for any other file.

If you're running with `--verbose`, you will see a blue message if a file was found and
used.

Please note `blackd` will not use `pyproject.toml` configuration.

### Configuration format

As the file extension suggests, `pyproject.toml` is a
[TOML](https://github.com/toml-lang/toml) file. It contains separate sections for
different tools. _Black_ is using the `[tool.black]` section. The option keys are the
same as long names of options on the command line.

Note that you have to use single-quoted strings in TOML for regular expressions. It's
the equivalent of r-strings in Python. Multiline strings are treated as verbose regular
expressions by Black. Use `[ ]` to denote a significant space character.

<details>
<summary>Example <code>pyproject.toml</code></summary>

```toml
[tool.black]
line-length = 88
target-version = ['py37']
include = '\.pyi?$'
exclude = '''

(
  /(
      \.eggs         # exclude a few common directories in the
    | \.git          # root of the project
    | \.hg
    | \.mypy_cache
    | \.tox
    | \.venv
    | _build
    | buck-out
    | build
    | dist
  )/
  | foo.py           # also separately exclude a file named foo.py in
                     # the root of the project
)
'''
```

</details>

### Lookup hierarchy

Command-line options have defaults that you can see in `--help`. A `pyproject.toml` can
override those defaults. Finally, options provided by the user on the command line
override both.

_Black_ will only ever use one `pyproject.toml` file during an entire run. It doesn't
look for multiple files, and doesn't compose configuration from different levels of the
file hierarchy.

## Editor integration

_Black_ can be integrated into many editors with plugins. They let you run _Black_ on
your code with the ease of doing it in your editor. To get started using _Black_ in your
editor of choice, please see
[editor_integration](https://github.com/psf/black/blob/master/docs/editor_integration.md).

Patches are welcome for editors without an editor integration or plugin! More
information can be found in
[editor_integration](https://github.com/psf/black/blob/master/docs/editor_integration.md#other-editors).

## blackd

`blackd` is a small HTTP server that exposes Black's functionality over a simple
protocol. The main benefit of using it is to avoid paying the cost of starting up a new
Black process every time you want to blacken a file. Please refer to
[blackd](https://github.com/psf/black/blob/master/docs/blackd.md) to get the ball
rolling.

## black-primer

`black-primer` is a tool built for CI (and humans) to have _Black_ `--check` a number of
(configured in `primer.json`) Git accessible projects in parallel.
[black_primer](https://github.com/psf/black/blob/master/docs/black_primer.md) has more
information regarding its usage and configuration.

(A PR adding Mercurial support will be accepted.)

## Version control integration

Use [pre-commit](https://pre-commit.com/). Once you
[have it installed](https://pre-commit.com/#install), add this to the
`.pre-commit-config.yaml` in your repository:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 19.10b0 # Replace by any tag/version: https://github.com/psf/black/tags
    hooks:
      - id: black
        language_version: python3 # Should be a command that runs python3.6+
```

Then run `pre-commit install` and you're ready to go.

Avoid using `args` in the hook. Instead, store necessary configuration in
`pyproject.toml` so that editors and command-line usage of Black all behave consistently
for your project. See _Black_'s own
[pyproject.toml](https://github.com/psf/black/blob/master/pyproject.toml) for an
example.

If you're already using Python 3.7, switch the `language_version` accordingly. Finally,
`stable` is a branch that tracks the latest release on PyPI. If you'd rather run on
master, this is also an option.

## GitHub Actions

Create a file named `.github/workflows/black.yml` inside your repository with:

```yaml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - uses: psf/black@stable
```

## Ignoring unmodified files

_Black_ remembers files it has already formatted, unless the `--diff` flag is used or
code is passed via standard input. This information is stored per-user. The exact
location of the file depends on the _Black_ version and the system on which _Black_ is
run. The file is non-portable. The standard location on common operating systems is:

- Windows:
  `C:\\Users\<username>\AppData\Local\black\black\Cache\<version>\cache.<line-length>.<file-mode>.pickle`
- macOS:
  `/Users/<username>/Library/Caches/black/<version>/cache.<line-length>.<file-mode>.pickle`
- Linux:
  `/home/<username>/.cache/black/<version>/cache.<line-length>.<file-mode>.pickle`

`file-mode` is an int flag that determines whether the file was formatted as 3.6+ only,
as .pyi, and whether string normalization was omitted.

To override the location of these files on macOS or Linux, set the environment variable
`XDG_CACHE_HOME` to your preferred location. For example, if you want to put the cache
in the directory you're running _Black_ from, set `XDG_CACHE_HOME=.cache`. _Black_ will
then write the above files to `.cache/black/<version>/`.

## Used by

The following notable open-source projects trust _Black_ with enforcing a consistent
code style: pytest, tox, Pyramid, Django Channels, Hypothesis, attrs, SQLAlchemy,
Poetry, PyPA applications (Warehouse, Bandersnatch, Pipenv, virtualenv), pandas, Pillow,
every Datadog Agent Integration, Home Assistant.

The following organizations use _Black_: Facebook, Dropbox, Mozilla, Quora.

Are we missing anyone? Let us know.

## Testimonials

**Dusty Phillips**,
[writer](https://smile.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=dusty+phillips):

> _Black_ is opinionated so you don't have to be.

**Hynek Schlawack**, [creator of `attrs`](https://www.attrs.org/), core developer of
Twisted and CPython:

> An auto-formatter that doesn't suck is all I want for Xmas!

**Carl Meyer**, [Django](https://www.djangoproject.com/) core developer:

> At least the name is good.

**Kenneth Reitz**, creator of [`requests`](http://python-requests.org/) and
[`pipenv`](https://readthedocs.org/projects/pipenv/):

> This vastly improves the formatting of our code. Thanks a ton!

## Show your style

Use the badge in your project's README.md:

```md
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
```

Using the badge in README.rst:

```
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
```

Looks like this:
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## License

MIT

## Contributing to _Black_

In terms of inspiration, _Black_ is about as configurable as _gofmt_. This is
deliberate.

Bug reports and fixes are always welcome! However, before you suggest a new feature or
configuration knob, ask yourself why you want it. If it enables better integration with
some workflow, fixes an inconsistency, speeds things up, and so on - go for it! On the
other hand, if your answer is "because I don't like a particular formatting" then you're
not ready to embrace _Black_ yet. Such changes are unlikely to get accepted. You can
still try but prepare to be disappointed.

More details can be found in
[CONTRIBUTING](https://github.com/psf/black/blob/master/CONTRIBUTING.md).

## Change log

The log's become rather long. It moved to its own file.

See [CHANGES](https://github.com/psf/black/blob/master/CHANGES.md).

## Authors

Glued together by [Łukasz Langa](mailto:lukasz@langa.pl).

Maintained with [Carol Willing](mailto:carolcode@willingconsulting.com),
[Carl Meyer](mailto:carl@oddbird.net),
[Jelle Zijlstra](mailto:jelle.zijlstra@gmail.com),
[Mika Naylor](mailto:mail@autophagy.io),
[Zsolt Dollenstein](mailto:zsol.zsol@gmail.com), and
[Cooper Lees](mailto:me@cooperlees.com).

Multiple contributions by:

- [Abdur-Rahmaan Janhangeer](mailto:arj.python@gmail.com)
- [Adam Johnson](mailto:me@adamj.eu)
- [Adam Williamson](mailto:adamw@happyassassin.net)
- [Alexander Huynh](mailto:github@grande.coffee)
- [Alex Vandiver](mailto:github@chmrr.net)
- [Allan Simon](mailto:allan.simon@supinfo.com)
- Anders-Petter Ljungquist
- [Andrew Thorp](mailto:andrew.thorp.dev@gmail.com)
- [Andrew Zhou](mailto:andrewfzhou@gmail.com)
- [Andrey](mailto:dyuuus@yandex.ru)
- [Andy Freeland](mailto:andy@andyfreeland.net)
- [Anthony Sottile](mailto:asottile@umich.edu)
- [Arjaan Buijk](mailto:arjaan.buijk@gmail.com)
- [Arnav Borbornah](mailto:arnavborborah11@gmail.com)
- [Artem Malyshev](mailto:proofit404@gmail.com)
- [Asger Hautop Drewsen](mailto:asgerdrewsen@gmail.com)
- [Augie Fackler](mailto:raf@durin42.com)
- [Aviskar KC](mailto:aviskarkc10@gmail.com)
- Batuhan Taşkaya
- [Benjamin Wohlwend](mailto:bw@piquadrat.ch)
- [Benjamin Woodruff](mailto:github@benjam.info)
- [Bharat Raghunathan](mailto:bharatraghunthan9767@gmail.com)
- [Brandt Bucher](mailto:brandtbucher@gmail.com)
- [Brett Cannon](mailto:brett@python.org)
- [Bryan Bugyi](mailto:bryan.bugyi@rutgers.edu)
- [Bryan Forbes](mailto:bryan@reigndropsfall.net)
- [Calum Lind](mailto:calumlind@gmail.com)
- [Charles](mailto:peacech@gmail.com)
- Charles Reid
- [Christian Clauss](mailto:cclauss@bluewin.ch)
- [Christian Heimes](mailto:christian@python.org)
- [Chuck Wooters](mailto:chuck.wooters@microsoft.com)
- [Chris Rose](mailto:offline@offby1.net)
- Codey Oxley
- [Cong](mailto:congusbongus@gmail.com)
- [Cooper Ry Lees](mailto:me@cooperlees.com)
- [Dan Davison](mailto:dandavison7@gmail.com)
- [Daniel Hahler](mailto:github@thequod.de)
- [Daniel M. Capella](mailto:polycitizen@gmail.com)
- Daniele Esposti
- [David Hotham](mailto:david.hotham@metaswitch.com)
- [David Lukes](mailto:dafydd.lukes@gmail.com)
- [David Szotten](mailto:davidszotten@gmail.com)
- [Denis Laxalde](mailto:denis@laxalde.org)
- [Douglas Thor](mailto:dthor@transphormusa.com)
- dylanjblack
- [Eli Treuherz](mailto:eli@treuherz.com)
- [Emil Hessman](mailto:emil@hessman.se)
- [Felix Kohlgrüber](mailto:felix.kohlgrueber@gmail.com)
- [Florent Thiery](mailto:fthiery@gmail.com)
- Francisco
- [Giacomo Tagliabue](mailto:giacomo.tag@gmail.com)
- [Greg Gandenberger](mailto:ggandenberger@shoprunner.com)
- [Gregory P. Smith](mailto:greg@krypto.org)
- Gustavo Camargo
- hauntsaninja
- [Heaford](mailto:dan@heaford.com)
- [Hugo Barrera](mailto::hugo@barrera.io)
- Hugo van Kemenade
- [Hynek Schlawack](mailto:hs@ox.cx)
- [Ivan Katanić](mailto:ivan.katanic@gmail.com)
- [Jakub Kadlubiec](mailto:jakub.kadlubiec@skyscanner.net)
- [Jakub Warczarek](mailto:jakub.warczarek@gmail.com)
- [Jan Hnátek](mailto:jan.hnatek@gmail.com)
- [Jason Fried](mailto:me@jasonfried.info)
- [Jason Friedland](mailto:jason@friedland.id.au)
- [jgirardet](mailto:ijkl@netc.fr)
- Jim Brännlund
- [Jimmy Jia](mailto:tesrin@gmail.com)
- [Joe Antonakakis](mailto:jma353@cornell.edu)
- [Jon Dufresne](mailto:jon.dufresne@gmail.com)
- [Jonas Obrist](mailto:ojiidotch@gmail.com)
- [Jonty Wareing](mailto:jonty@jonty.co.uk)
- [Jose Nazario](mailto:jose.monkey.org@gmail.com)
- [Joseph Larson](mailto:larson.joseph@gmail.com)
- [Josh Bode](mailto:joshbode@fastmail.com)
- [Josh Holland](mailto:anowlcalledjosh@gmail.com)
- [José Padilla](mailto:jpadilla@webapplicate.com)
- [Juan Luis Cano Rodríguez](mailto:hello@juanlu.space)
- [kaiix](mailto:kvn.hou@gmail.com)
- [Katie McLaughlin](mailto:katie@glasnt.com)
- Katrin Leinweber
- [Keith Smiley](mailto:keithbsmiley@gmail.com)
- [Kenyon Ralph](mailto:kenyon@kenyonralph.com)
- [Kevin Kirsche](mailto:Kev.Kirsche+GitHub@gmail.com)
- [Kyle Hausmann](mailto:kyle.hausmann@gmail.com)
- [Kyle Sunden](mailto:sunden@wisc.edu)
- Lawrence Chan
- [Linus Groh](mailto:mail@linusgroh.de)
- [Loren Carvalho](mailto:comradeloren@gmail.com)
- [Luka Sterbic](mailto:luka.sterbic@gmail.com)
- [LukasDrude](mailto:mail@lukas-drude.de)
- Mahmoud Hossam
- Mariatta
- [Matt VanEseltine](mailto:vaneseltine@gmail.com)
- [Matthew Clapp](mailto:itsayellow+dev@gmail.com)
- [Matthew Walster](mailto:matthew@walster.org)
- Max Smolens
- [Michael Aquilina](mailto:michaelaquilina@gmail.com)
- [Michael Flaxman](mailto:michael.flaxman@gmail.com)
- [Michael J. Sullivan](mailto:sully@msully.net)
- [Michael McClimon](mailto:michael@mcclimon.org)
- [Miguel Gaiowski](mailto:miggaiowski@gmail.com)
- [Mike](mailto:roshi@fedoraproject.org)
- [mikehoyio](mailto:mikehoy@gmail.com)
- [Min ho Kim](mailto:minho42@gmail.com)
- [Miroslav Shubernetskiy](mailto:miroslav@miki725.com)
- MomIsBestFriend
- [Nathan Goldbaum](mailto:ngoldbau@illinois.edu)
- [Nathan Hunt](mailto:neighthan.hunt@gmail.com)
- [Neraste](mailto:neraste.herr10@gmail.com)
- [Nikolaus Waxweiler](mailto:madigens@gmail.com)
- [Ofek Lev](mailto:ofekmeister@gmail.com)
- [Osaetin Daniel](mailto:osaetindaniel@gmail.com)
- [otstrel](mailto:otstrel@gmail.com)
- [Pablo Galindo](mailto:Pablogsal@gmail.com)
- [Paul Ganssle](mailto:p.ganssle@gmail.com)
- [Paul Meinhardt](mailto:mnhrdt@gmail.com)
- [Peter Bengtsson](mailto:mail@peterbe.com)
- [Peter Stensmyr](mailto:peter.stensmyr@gmail.com)
- pmacosta
- [Quentin Pradet](mailto:quentin@pradet.me)
- [Ralf Schmitt](mailto:ralf@systemexit.de)
- [Ramón Valles](mailto:mroutis@protonmail.com)
- [Richard Fearn](mailto:richardfearn@gmail.com)
- Richard Si
- [Rishikesh Jha](mailto:rishijha424@gmail.com)
- [Rupert Bedford](mailto:rupert@rupertb.com)
- Russell Davis
- [Rémi Verschelde](mailto:rverschelde@gmail.com)
- [Sami Salonen](mailto:sakki@iki.fi)
- [Samuel Cormier-Iijima](mailto:samuel@cormier-iijima.com)
- [Sanket Dasgupta](mailto:sanketdasgupta@gmail.com)
- Sergi
- [Scott Stevenson](mailto:scott@stevenson.io)
- Shantanu
- [shaoran](mailto:shaoran@sakuranohana.org)
- [Shinya Fujino](mailto:shf0811@gmail.com)
- springstan
- [Stavros Korokithakis](mailto:hi@stavros.io)
- [Stephen Rosen](mailto:sirosen@globus.org)
- [Steven M. Vascellaro](mailto:S.Vascellaro@gmail.com)
- [Sunil Kapil](mailto:snlkapil@gmail.com)
- [Sébastien Eustace](mailto:sebastien.eustace@gmail.com)
- [Tal Amuyal](mailto:TalAmuyal@gmail.com)
- [Terrance](mailto:git@terrance.allofti.me)
- [Thom Lu](mailto:thomas.c.lu@gmail.com)
- [Thomas Grainger](mailto:tagrain@gmail.com)
- [Tim Gates](mailto:tim.gates@iress.com)
- [Tim Swast](mailto:swast@google.com)
- [Timo](mailto:timo_tk@hotmail.com)
- Toby Fleming
- [Tom Christie](mailto:tom@tomchristie.com)
- [Tony Narlock](mailto:tony@git-pull.com)
- [Tsuyoshi Hombashi](mailto:tsuyoshi.hombashi@gmail.com)
- [Tushar Chandra](mailto:tusharchandra2018@u.northwestern.edu)
- [Tzu-ping Chung](mailto:uranusjr@gmail.com)
- [Utsav Shah](mailto:ukshah2@illinois.edu)
- utsav-dbx
- vezeli
- [Ville Skyttä](mailto:ville.skytta@iki.fi)
- [Vishwas B Sharma](mailto:sharma.vishwas88@gmail.com)
- [Vlad Emelianov](mailto:volshebnyi@gmail.com)
- [williamfzc](mailto:178894043@qq.com)
- [wouter bolsterlee](mailto:wouter@bolsterl.ee)
- Yazdan
- [Yngve Høiseth](mailto:yngve@hoiseth.net)
- [Yurii Karabas](mailto:1998uriyyo@gmail.com)
- [Zac Hatfield-Dodds](mailto:zac@zhd.dev)
