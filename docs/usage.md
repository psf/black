# Installation and Usage

## Installation

*Black* can be installed by running `pip install black`.

## Usage

To get started right away with sensible defaults:

```
black {source_file}
```

### Command line options

Some basics about the command line help, `black --help`:

```
Usage: black [OPTIONS] [SRC]...

  The uncompromising code formatter.

Options:
  -l, --line-length INTEGER  How many character per line to allow.  [default:
                             88]
  --check                    Don't write back the files, just return the
                             status.  Return code 0 means nothing would
                             change.  Return code 1 means some files would be
                             reformatted.  Return code 123 means there was an
                             internal error.
  --fast / --safe            If --fast given, skip temporary sanity checks.
                             [default: --safe]
  --version                  Show the version and exit.
  --help                     Show this message and exit.
```

`Black` is a well-behaved Unix-style command-line tool:

* it does nothing if no sources are passed to it;
* it will read from standard input and write to standard output if `-`
  is used as the filename;
* it only outputs messages to users on standard error;
* exits with code 0 unless an internal error occured (or `--check` was
  used).

## Important note about the pre-release of Black

*Black* can already successfully format itself and the standard library.
It also sports a decent test suite.  However, it is still very new.
Things will probably be wonky for a while. This is made explicit by the
"Alpha" trove classifier, as well as by the "a" in the version number.
What this means for you is that **until the formatter becomes stable,
you should expect some formatting to change in the future**.

Also, as a temporary safety measure, *Black* will check that the
reformatted code still produces a valid AST that is equivalent to the
original.  This slows it down.  If you're feeling confident, use
``--fast``.
