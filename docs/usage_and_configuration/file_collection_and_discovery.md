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
- macOS: `/Users/<username>/Library/Caches/black/<version>/cache.<mode-key>.pickle`
- Linux: `/home/<username>/.cache/black/<version>/cache.<mode-key>.pickle`

`mode-key` identifies the formatting options used for the cached files. Formatting with
different options uses a different cache file.

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

By default, _Black_ uses `.gitignore` files during recursive discovery when `--exclude`
is unset. Use `--extend-exclude` to add patterns to the default exclusions while still
using `.gitignore`.

To replace the default exclusions and still use `.gitignore`, combine `--exclude` with
`--respect-gitignore`. For example, this `pyproject.toml` lets _Black_ discover Python
files in a package named `build` while skipping `.git` and paths listed in `.gitignore`.

```toml
[tool.black]
exclude = '/\.git/'
respect-gitignore = true
```

Use `--no-respect-gitignore` or `respect-gitignore = false` to disable `.gitignore`
handling independently of the exclusion regex.
