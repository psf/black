# The basics

Foundational knowledge on using and configuring Black.

_Black_ is a well-behaved Unix-style command-line tool:

- it does nothing if no sources are passed to it;
- it will read from standard input and write to standard output if `-` is used as the
  filename;
- it only outputs messages to users on standard error;
- exits with code 0 unless an internal error occurred (or `--check` was used).

## Usage

To get started right away with sensible defaults:

```sh
black {source_file_or_directory}
```

You can run _Black_ as a package if running it as a script doesn't work:

```sh
python -m black {source_file_or_directory}
```

### Command line options

_Black_ has quite a few knobs these days, although _Black_ is opinionated so style
configuration options are deliberately limited and rarely added. You can list them by
running `black --help`.

<details>

<summary>Help output</summary>

```
  Usage: black [OPTIONS] [SRC]...

    The uncompromising code formatter.

  Options:
    -c, --code TEXT                 Format the code passed in as a string.
    -l, --line-length INTEGER       How many characters per line to allow.
                                    [default: 88]

    -t, --target-version [py27|py33|py34|py35|py36|py37|py38|py39]
                                    Python versions that should be supported by
                                    Black's output. [default: per-file auto-
                                    detection]

    --pyi                           Format all input files like typing stubs
                                    regardless of file extension (useful when
                                    piping source on standard input).

    -S, --skip-string-normalization
                                    Don't normalize string quotes or prefixes.
    -C, --skip-magic-trailing-comma
                                    Don't use trailing commas as a reason to
                                    split lines.

    --check                         Don't write the files back, just return the
                                    status. Return code 0 means nothing would
                                    change. Return code 1 means some files
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
                                    recursive searches. An empty value means
                                    all files are included regardless of the
                                    name. Use forward slashes for directories
                                    on all platforms (Windows, too). Exclusions
                                    are calculated first, inclusions later.
                                    [default: \.pyi?$]

    --exclude TEXT                  A regular expression that matches files and
                                    directories that should be excluded on
                                    recursive searches. An empty value means no
                                    paths are excluded. Use forward slashes for
                                    directories on all platforms (Windows, too).
                                    Exclusions are calculated first, inclusions
                                    later.  [default: /(\.direnv|\.eggs|\.git|\.
                                    hg|\.mypy_cache|\.nox|\.tox|\.venv|venv|\.svn|_bu
                                    ild|buck-out|build|dist)/]

    --extend-exclude TEXT           Like --exclude, but adds additional files
                                    and directories on top of the excluded
                                    ones (useful if you simply want to add to
                                    the default).

    --force-exclude TEXT            Like --exclude, but files and directories
                                    matching this regex will be excluded even
                                    when they are passed explicitly as
                                    arguments.


    --stdin-filename TEXT           The name of the file when passing it through
                                    stdin. Useful to make sure Black will
                                    respect --force-exclude option on some
                                    editors that rely on using stdin.

    -q, --quiet                     Don't emit non-error messages to stderr.
                                    Errors are still emitted; silence those with
                                    2>/dev/null.

    -v, --verbose                   Also emit messages to stderr about files
                                    that were not changed or were ignored due to
                                    exclusion patterns.

    --version                       Show the version and exit.
    --config FILE                   Read configuration from FILE path.
    -h, --help                      Show this message and exit.
```

</details>

## Configuration via a file

_Black_ is able to read project-specific default values for its command line options
from a `pyproject.toml` file. This is especially useful for specifying custom
`--include` and `--exclude`/`--force-exclude`/`--extend-exclude` patterns for your
project.

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

You can use a "global" configuration, stored in a specific location in your home
directory. This will be used as a fallback configuration, that is, it will be used if
and only if _Black_ doesn't find any configuration as mentioned above. Depending on your
operating system, this configuration file should be stored as:

- Windows: `~\.black`
- Unix-like (Linux, MacOS, etc.): `$XDG_CONFIG_HOME/black` (`~/.config/black` if the
  `XDG_CONFIG_HOME` environment variable is not set)

Note that these are paths to the TOML file itself (meaning that they shouldn't be named
as `pyproject.toml`), not directories where you store the configuration. Here, `~`
refers to the path to your home directory. On Windows, this will be something like
`C:\\Users\UserName`.

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
extend-exclude = '''
# A regex preceded with ^/ will apply only to files and directories
# in the root of the project.
^/foo.py  # exclude a file named foo.py in the root of the project (in addition to the defaults)
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

## Next steps

You've probably noted that not all of the options you can pass to _Black_ have been
covered. Don't worry, the rest will be covered in a later section.

A good next step would be configuring auto-discovery so `black .` is all you need
instead of laborously listing every file or directory. You can get started by heading
over to [File collection and discovery](./file_collection_and_discovery.md).

Another good choice would be setting up an
[integration with your editor](../integrations/editors.md) of choice or with
[pre-commit for source version control](../integrations/source_version_control.md).
