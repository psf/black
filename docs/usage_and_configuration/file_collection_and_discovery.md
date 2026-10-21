# File collection and discovery

You can directly pass _Black_ files, but you can also pass directories and _Black_ will
walk them, collecting files to format. It determines what files to format or skip
automatically using the inclusion and exclusion regexes and as well their modification
time.

## Ignoring unmodified files

_Black_ remembers files it has already formatted, unless code is passed via standard
input or the `--no-cache` flag is used. This information is stored per-user. The exact
location of the file depends on the _Black_ version and the system on which _Black_ is
run. The file is non-portable. The standard location on common operating systems is:

- Windows:
  `C:\Users\<username>\AppData\Local\black\black\Cache\<version>\cache.<mode-key>.pickle`
- macOS:
  `/Users/<username>/Library/Caches/black/<version>/cache.<mode-key>.pickle`
- Linux:
  `/home/<username>/.cache/black/<version>/cache.<mode-key>.pickle`

`mode-key` is built by `Mode.get_cache_key()`: a dot-separated list of the settings the
files were formatted with — the target versions, the line length, and `1`/`0` values for
string normalization, `.pyi` mode, notebook mode, `--skip-source-first-line`,
`--magic-trailing-comma`, `--preview` and `--unstable` — followed by a short hash of the
enabled preview features and the cell magics. Formatting with different options therefore
reads and writes a different cache file. A default run on a source file produces a name
like `cache.-.88.1.0.0.0.1.0.0.c3641f8544d7c02f3580b07c0f9887f0.pickle`.

To override the location of these files on all systems, pass `--cache-dir` or set the
environment variable `BLACK_CACHE_DIR` to the preferred location. Alternatively on macOS
and Linux, set `XDG_CACHE_HOME` to your preferred location. For example, if you want to
put the cache in the directory you're running _Black_ from, pass
`--cache-dir=.cache/black` or set `BLACK_CACHE_DIR=.cache/black`. _Black_ will then
write the above files to `.cache/black`. The command-line option takes precedence over
`BLACK_CACHE_DIR`, which takes precedence over `XDG_CACHE_HOME`.

### Disabling the cache with --no-cache

If you need Black to always perform a fresh analysis and not consult or update the
on-disk cache, use the `--no-cache` flag. When provided, Black will neither read from
nor write to the per-user cache. This is useful for debugging, for CI runs where you
want a deterministic fresh run, or when you suspect cache corruption. If combined with
`--cache-dir`, `--no-cache` takes precedence and the specified cache directory is not
created or used.

Example:

```console
python -m black --no-cache .
```

## .gitignore

If `--exclude` is not set, _Black_ will automatically ignore files and directories in
`.gitignore` file(s), if present.

If you want _Black_ to continue using `.gitignore` while also configuring the exclusion
rules, please use `--extend-exclude`.
