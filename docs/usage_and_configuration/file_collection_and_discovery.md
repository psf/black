# File collection and discovery

You can directly pass _Black_ files, but you can also pass directories and _Black_ will
walk them, collecting files to format. It determines what files to format or skip
automatically using the inclusion and exclusion regexes and as well their modification
time.

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

To override the location of these files on all systems, set the environment variable
`BLACK_CACHE_DIR` to the preferred location. Alternatively on macOS and Linux, set
`XDG_CACHE_HOME` to your preferred location. For example, if you want to put the cache
in the directory you're running _Black_ from, set `BLACK_CACHE_DIR=.cache/black`.
_Black_ will then write the above files to `.cache/black`. Note that `BLACK_CACHE_DIR`
will take precedence over `XDG_CACHE_HOME` if both are set.

## .gitignore

If `--exclude` is not set, _Black_ will automatically ignore files and directories in
`.gitignore` file(s), if present.

If you want _Black_ to continue using `.gitignore` while also configuring the exclusion
rules, please use `--extend-exclude`.
