# The basics

Foundational knowledge on using and configuring Black.

_Black_ is a well-behaved Unix-style command-line tool:

- it does nothing if it finds no sources to format;
- it will read from standard input and write to standard output if `-` is used as the
  filename;
- it only outputs messages to users on standard error;
- exits with code 0 unless an internal error occurred or a CLI option prompted it.

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

The CLI options of _Black_ can be displayed by running `black --help`. All options are
also covered in more detail below.

While _Black_ has quite a few knobs these days, it is still opinionated so style options
are deliberately limited and rarely added.

Note that all command-line options listed above can also be configured using a
`pyproject.toml` file (more on that below).

#### `-c`, `--code`

Format the code passed in as a string.

```console
$ black --code "print ( 'hello, world' )"
print("hello, world")
```

#### `-l`, `--line-length`

How many characters per line to allow. The default is 88.

See also [the style documentation](labels/line-length).

#### `-t`, `--target-version`

Python versions that should be supported by Black's output. You can run `black --help`
and look for the `--target-version` option to see the full list of supported versions.
You should include all versions that your code supports. If you support Python 3.8
through 3.11, you should write:

```console
$ black -t py38 -t py39 -t py310 -t py311
```

In a [configuration file](#configuration-via-a-file), you can write:

```toml
target-version = ["py38", "py39", "py310", "py311"]
```

_Black_ uses this option to decide what grammar to use to parse your code. In addition,
it may use it to decide what style to use. For example, support for a trailing comma
after `*args` in a function call was added in Python 3.5, so _Black_ will add this comma
only if the target versions are all Python 3.5 or higher:

```console
$ black --line-length=10 --target-version=py35 -c 'f(a, *args)'
f(
    a,
    *args,
)
$ black --line-length=10 --target-version=py34 -c 'f(a, *args)'
f(
    a,
    *args
)
$ black --line-length=10 --target-version=py34 --target-version=py35 -c 'f(a, *args)'
f(
    a,
    *args
)
```

#### `--pyi`

Format all input files like typing stubs regardless of file extension. This is useful
when piping source on standard input.

#### `--ipynb`

Format all input files like Jupyter Notebooks regardless of file extension. This is
useful when piping source on standard input.

#### `--python-cell-magics`

When processing Jupyter Notebooks, add the given magic to the list of known python-
magics. Useful for formatting cells with custom python magics.

#### `-S, --skip-string-normalization`

By default, _Black_ uses double quotes for all strings and normalizes string prefixes,
as described in [the style documentation](labels/strings). If this option is given,
strings are left unchanged instead.

#### `-C, --skip-magic-trailing-comma`

By default, _Black_ uses existing trailing commas as an indication that short lines
should be left separate, as described in
[the style documentation](labels/magic-trailing-comma). If this option is given, the
magic trailing comma is ignored.

#### `--preview`

Enable potentially disruptive style changes that may be added to Black's main
functionality in the next major release. Read more about
[our preview style](labels/preview-style).

(labels/exit-code)=

#### `--check`

Passing `--check` will make _Black_ exit with:

- code 0 if nothing would change;
- code 1 if some files would be reformatted; or
- code 123 if there was an internal error

```console
$ black test.py --check
All done! ✨ 🍰 ✨
1 file would be left unchanged.
$ echo $?
0

$ black test.py --check
would reformat test.py
Oh no! 💥 💔 💥
1 file would be reformatted.
$ echo $?
1

$ black test.py --check
error: cannot format test.py: INTERNAL ERROR: Black produced code that is not equivalent to the source.  Please report a bug on https://github.com/psf/black/issues.  This diff might be helpful: /tmp/blk_kjdr1oog.log
Oh no! 💥 💔 💥
1 file would fail to reformat.
$ echo $?
123
```

#### `--diff`

Passing `--diff` will make _Black_ print out diffs that indicate what changes _Black_
would've made. They are printed to stdout so capturing them is simple.

If you'd like colored diffs, you can enable them with `--color`.

```console
$ black test.py --diff
--- test.py     2021-03-08 22:23:40.848954+00:00
+++ test.py     2021-03-08 22:23:47.126319+00:00
@@ -1 +1 @@
-print ( 'hello, world' )
+print("hello, world")
would reformat test.py
All done! ✨ 🍰 ✨
1 file would be reformatted.
```

#### `--color` / `--no-color`

Show (or do not show) colored diff. Only applies when `--diff` is given.

#### `--fast` / `--safe`

By default, _Black_ performs [an AST safety check](labels/ast-changes) after formatting
your code. The `--fast` flag turns off this check and the `--safe` flag explicitly
enables it.

#### `--required-version`

Require a specific version of _Black_ to be running. This is useful for ensuring that
all contributors to your project are using the same version, because different versions
of _Black_ may format code a little differently. This option can be set in a
configuration file for consistent results across environments.

```console
$ black --version
black, 23.10.0 (compiled: yes)
$ black --required-version 23.10.0 -c "format = 'this'"
format = "this"
$ black --required-version 31.5b2 -c "still = 'beta?!'"
Oh no! 💥 💔 💥 The required version does not match the running version!
```

You can also pass just the major version:

```console
$ black --required-version 22 -c "format = 'this'"
format = "this"
$ black --required-version 31 -c "still = 'beta?!'"
Oh no! 💥 💔 💥 The required version does not match the running version!
```

Because of our [stability policy](../the_black_code_style/index.md), this will guarantee
stable formatting, but still allow you to take advantage of improvements that do not
affect formatting.

#### `--include`

A regular expression that matches files and directories that should be included on
recursive searches. An empty value means all files are included regardless of the name.
Use forward slashes for directories on all platforms (Windows, too). Exclusions are
calculated first, inclusions later.

#### `--exclude`

A regular expression that matches files and directories that should be excluded on
recursive searches. An empty value means no paths are excluded. Use forward slashes for
directories on all platforms (Windows, too). Exclusions are calculated first, inclusions
later.

#### `--extend-exclude`

Like `--exclude`, but adds additional files and directories on top of the excluded ones.
Useful if you simply want to add to the default.

#### `--force-exclude`

Like `--exclude`, but files and directories matching this regex will be excluded even
when they are passed explicitly as arguments. This is useful when invoking _Black_
programmatically on changed files, such as in a pre-commit hook or editor plugin.

#### `--stdin-filename`

The name of the file when passing it through stdin. Useful to make sure Black will
respect the `--force-exclude` option on some editors that rely on using stdin.

#### `-W`, `--workers`

When _Black_ formats multiple files, it may use a process pool to speed up formatting.
This option controls the number of parallel workers. This can also be specified via the
`BLACK_NUM_WORKERS` environment variable.

#### `-q`, `--quiet`

Passing `-q` / `--quiet` will cause _Black_ to stop emitting all non-critical output.
Error messages will still be emitted (which can silenced by `2>/dev/null`).

```console
$ black src/ -q
error: cannot format src/black_primer/cli.py: Cannot parse: 5:6: mport asyncio
```

#### `-v`, `--verbose`

Passing `-v` / `--verbose` will cause _Black_ to also emit messages about files that
were not changed or were ignored due to exclusion patterns. If _Black_ is using a
configuration file, a blue message detailing which one it is using will be emitted.

```console
$ black src/ -v
Using configuration from /tmp/pyproject.toml.
src/blib2to3 ignored: matches the --extend-exclude regular expression
src/_black_version.py wasn't modified on disk since last run.
src/black/__main__.py wasn't modified on disk since last run.
error: cannot format src/black_primer/cli.py: Cannot parse: 5:6: mport asyncio
reformatted src/black_primer/lib.py
reformatted src/blackd/__init__.py
reformatted src/black/__init__.py
Oh no! 💥 💔 💥
3 files reformatted, 2 files left unchanged, 1 file failed to reformat
```

#### `--version`

You can check the version of _Black_ you have installed using the `--version` flag.

```console
$ black --version
black, 23.10.0
```

#### `--config`

Read configuration options from a configuration file. See
[below](#configuration-via-a-file) for more details on the configuration file.

#### `-h`, `--help`

Show available command-line options and exit.

### Environment variable options

_Black_ supports the following configuration via environment variables.

#### `BLACK_CACHE_DIR`

The directory where _Black_ should store its cache.

#### `BLACK_NUM_WORKERS`

The number of parallel workers _Black_ should use. The command line option `-W` /
`--workers` takes precedence over this environment variable.

### Code input alternatives

_Black_ supports formatting code via stdin, with the result being printed to stdout.
Just let _Black_ know with `-` as the path.

```console
$ echo "print ( 'hello, world' )" | black -
print("hello, world")
reformatted -
All done! ✨ 🍰 ✨
1 file reformatted.
```

**Tip:** if you need _Black_ to treat stdin input as a file passed directly via the CLI,
use `--stdin-filename`. Useful to make sure _Black_ will respect the `--force-exclude`
option on some editors that rely on using stdin.

You can also pass code as a string using the `-c` / `--code` option.

### Writeback and reporting

By default _Black_ reformats the files given and/or found in place. Sometimes you need
_Black_ to just tell you what it _would_ do without actually rewriting the Python files.

There's two variations to this mode that are independently enabled by their respective
flags:

- `--check` (exit with code 1 if any file would be reformatted)
- `--diff` (print a diff instead of reformatting files)

Both variations can be enabled at once.

### Output verbosity

_Black_ in general tries to produce the right amount of output, balancing between
usefulness and conciseness. By default, _Black_ emits files modified and error messages,
plus a short summary.

```console
$ black src/
error: cannot format src/black_primer/cli.py: Cannot parse: 5:6: mport asyncio
reformatted src/black_primer/lib.py
reformatted src/blackd/__init__.py
reformatted src/black/__init__.py
Oh no! 💥 💔 💥
3 files reformatted, 2 files left unchanged, 1 file failed to reformat.
```

The `--quiet` and `--verbose` flags control output verbosity.

## Configuration via a file

_Black_ is able to read project-specific default values for its command line options
from a `pyproject.toml` file. This is especially useful for specifying custom
`--include` and `--exclude`/`--force-exclude`/`--extend-exclude` patterns for your
project.

**Pro-tip**: If you're asking yourself "Do I need to configure anything?" the answer is
"No". _Black_ is all about sensible defaults. Applying those defaults will have your
code in compliance with many other _Black_ formatted projects.

### What on Earth is a `pyproject.toml` file?

[PEP 518](https://www.python.org/dev/peps/pep-0518/) defines `pyproject.toml` as a
configuration file to store build system requirements for Python projects. With the help
of tools like [Poetry](https://python-poetry.org/),
[Flit](https://flit.readthedocs.io/en/latest/), or
[Hatch](https://hatch.pypa.io/latest/) it can fully replace the need for `setup.py` and
`setup.cfg` files.

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
# 'extend-exclude' excludes files or directories in addition to the defaults
extend-exclude = '''
# A regex preceded with ^/ will apply only to files and directories
# in the root of the project.
(
  ^/foo.py    # exclude a file named foo.py in the root of the project
  | .*_pb2.py  # exclude autogenerated Protocol Buffer files anywhere in the project
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

## Next steps

A good next step would be configuring auto-discovery so `black .` is all you need
instead of laborously listing every file or directory. You can get started by heading
over to [File collection and discovery](./file_collection_and_discovery.md).

Another good choice would be setting up an
[integration with your editor](../integrations/editors.md) of choice or with
[pre-commit for source version control](../integrations/source_version_control.md).
