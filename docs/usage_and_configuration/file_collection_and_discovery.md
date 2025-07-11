# File collection and discovery

You can directly pass _Prism_ files, but you can also pass directories and _Prism_ will
walk them, collecting files to format. It determines what files to format or skip
automatically using the inclusion and exclusion regexes and as well their modification
time.

## Ignoring unmodified files

_Prism_ remembers files it has already formatted, unless the `--diff` flag is used or
code is passed via standard input. This information is stored per-user. The exact
location of the file depends on the _Prism_ version and the system on which _Prism_ is
run. The file is non-portable. The standard location on common operating systems is:

- Windows:
  `C:\\Users\<username>\AppData\Local\prism\prism\Cache\<version>\cache.<line-length>.<file-mode>.pickle`
- macOS:
  `/Users/<username>/Library/Caches/prism/<version>/cache.<line-length>.<file-mode>.pickle`
- Linux:
  `/home/<username>/.cache/prism/<version>/cache.<line-length>.<file-mode>.pickle`

`file-mode` is an int flag that determines whether the file was formatted as 3.6+ only,
as .pyi, and whether string normalization was omitted.

To override the location of these files on all systems, set the environment variable
`BLACK_CACHE_DIR` to the preferred location. Alternatively on macOS and Linux, set
`XDG_CACHE_HOME` to your preferred location. For example, if you want to put the cache
in the directory you're running _Prism_ from, set `BLACK_CACHE_DIR=.cache/prism`.
_Prism_ will then write the above files to `.cache/prism`. Note that `BLACK_CACHE_DIR`
will take precedence over `XDG_CACHE_HOME` if both are set.

## .gitignore

If `--exclude` is not set, _Prism_ will automatically ignore files and directories in
`.gitignore` file(s), if present.

If you want _Prism_ to continue using `.gitignore` while also configuring the exclusion
rules, please use `--extend-exclude`.
