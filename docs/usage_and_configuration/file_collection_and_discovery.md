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

### Disabling the cache with --no-cache

If you need Black to always perform a fresh analysis and not consult or update the
on-disk cache, use the `--no-cache` flag. When provided, Black will neither read from
nor write to the per-user cache. This is useful for debugging, for CI runs where you
want a deterministic fresh run, or when you suspect cache corruption.

Example:

python -m black --no-cache .

## .gitignore

If `--exclude` is not set, _Black_ will automatically ignore files and directories in
`.gitignore` file(s), if present.

If you want _Black_ to continue using `.gitignore` while also configuring the exclusion
rules, please use `--extend-exclude`.

## Explain mode

_Black_ provides an `--explain` (`-E`) flag that shows why each candidate path was
included for formatting or ignored. This is useful for debugging file collection issues
and understanding how your configuration affects which files get formatted.

### Basic usage

```bash
black --explain .
```

Output shows each path with a `+` (included) or `-` (ignored) prefix, along with a reason
code:

```
+ src/main.py [DISCOVERED_VIA_WALK]: discovered via directory walk (source: --include pattern)
- src/data.bin [NOT_INCLUDED]: does not match --include pattern (source: --include)
- .git [EXTEND_EXCLUDE_REGEX]: matches --extend-exclude (source: --extend-exclude)
```

### Reason codes

| Code | Description |
|------|-------------|
| `GITIGNORE_MATCH` | Path matched a `.gitignore` pattern |
| `EXCLUDE_REGEX` | Path matched `--exclude` regular expression |
| `EXTEND_EXCLUDE_REGEX` | Path matched `--extend-exclude` regular expression |
| `FORCE_EXCLUDE_REGEX` | Path matched `--force-exclude` regular expression |
| `STDIN_FORCE_EXCLUDE` | `--stdin-filename` matched `--force-exclude` |
| `CANNOT_STAT` | Path could not be stat'd or resolves outside root |
| `SYMLINK_OUTSIDE_ROOT` | Symlink resolves outside project root |
| `NOT_FILE_OR_DIR` | Path is neither file nor directory |
| `INVALID_PATH` | Path is not a valid source |
| `JUPYTER_DEPS_MISSING` | Jupyter dependencies not installed for `.ipynb` |
| `NOT_INCLUDED` | File does not match `--include` pattern |
| `EXPLICIT_FILE` | Explicit file path argument |
| `EXPLICIT_STDIN` | Stdin input (via `-`) |
| `EXPLICIT_STDIN_FILENAME` | Stdin with `--stdin-filename` |
| `DISCOVERED_VIA_WALK` | Discovered via directory walk |

### Output formats

Control the output format with `--explain-format`:

- `text` (default): Human-readable lines with `+`/`-` prefixes
- `json`: Full JSON object with all entries
- `jsonl`: One JSON object per line

```bash
black --explain --explain-format json .
```

### Filtering output

Use `--explain-show` to filter entries:

- `all` (default): Show both included and ignored paths
- `included`: Show only included paths
- `ignored`: Show only ignored paths

### Limiting output

Use `--explain-limit` to cap the number of entries shown:

```bash
black --explain --explain-limit 10 .
```

### Simulate mode

Use `--explain-simulate` to run file discovery and explain output without formatting
any files. This is useful for testing your configuration:

```bash
black --explain-simulate .
```

This implies `--explain` and exits after showing the explain report without running the
formatter.
