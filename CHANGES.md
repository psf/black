# Change Log

## Unreleased

### Highlights

<!-- Include any especially major or disruptive changes here -->

### Stable style

<!-- Changes that affect Black's stable style -->

- Fix crash while formatting a long `del` statement containing tuples (#4628)
- Fix crash while formatting expressions using the walrus operator in complex `with`
  statements (#4630)
- Handle `# fmt: skip` followed by a comment at the end of file (#4635)
- Fix crash when a tuple appears in the `as` clause of a `with` statement (#4634)
- Fix crash when tuple is used as a context manager inside a `with` statement (#4646)
- Fix crash when formatting a `\` followed by a `\r` followed by a comment (#4663)
- Fix crash on a `\\r\n` (#4673)
- Fix crash on `await ...` (where `...` is a literal `Ellipsis`) (#4676)
- Remove support for pre-python 3.7 `await/async` as soft keywords/variable names
  (#4676)
- Fix crash on parenthesized expression inside a type parameter bound (#4684)

### Preview style

<!-- Changes that affect Black's preview style -->

- Fix a bug where one-liner functions/conditionals marked with `# fmt: skip` would still
  be formatted (#4552)
- Improve `multiline_string_handling` with ternaries and dictionaries (#4657)
- Fix a bug where `string_processing` would not split f-strings directly after
  expressions (#4680)

### Configuration

<!-- Changes to how Black can be configured -->

### Packaging

<!-- Changes to how Black is packaged, such as dependency requirements -->

### Parser

<!-- Changes to the parser or to version autodetection -->

- Rewrite tokenizer to improve performance and compliance (#4536)
- Fix bug where certain unusual expressions (e.g., lambdas) were not accepted in type
  parameter bounds and defaults. (#4602)

### Performance

<!-- Changes that improve Black's performance. -->

### Output

<!-- Changes to Black's terminal output and error messages -->

### _Blackd_

<!-- Changes to blackd -->

### Integrations

<!-- For example, Docker, GitHub Actions, pre-commit, editors -->

- Fix the version check in the vim file to reject Python 3.8 (#4567)
- Enhance GitHub Action `psf/black` to read Black version from an additional section in
  pyproject.toml: `[project.dependency-groups]` (#4606)
- Build gallery docker image with python3-slim and reduce image size (#4686)

### Documentation

<!-- Major changes to documentation and policies. Small docs changes
     don't need a changelog entry. -->

- Add FAQ entry for windows emoji not displaying (#4714)

## 25.1.0

### Highlights

This release introduces the new 2025 stable style (#4558), stabilizing the following
changes:

- Normalize casing of Unicode escape characters in strings to lowercase (#2916)
- Fix inconsistencies in whether certain strings are detected as docstrings (#4095)
- Consistently add trailing commas to typed function parameters (#4164)
- Remove redundant parentheses in if guards for case blocks (#4214)
- Add parentheses to if clauses in case blocks when the line is too long (#4269)
- Whitespace before `# fmt: skip` comments is no longer normalized (#4146)
- Fix line length computation for certain expressions that involve the power operator
  (#4154)
- Check if there is a newline before the terminating quotes of a docstring (#4185)
- Fix type annotation spacing between `*` and more complex type variable tuple (#4440)

The following changes were not in any previous release:

- Remove parentheses around sole list items (#4312)
- Generic function definitions are now formatted more elegantly: parameters are split
  over multiple lines first instead of type parameter definitions (#4553)

### Stable style

- Fix formatting cells in IPython notebooks with magic methods and starting or trailing
  empty lines (#4484)
- Fix crash when formatting `with` statements containing tuple generators/unpacking
  (#4538)

### Preview style

- Fix/remove string merging changing f-string quotes on f-strings with internal quotes
  (#4498)
- Collapse multiple empty lines after an import into one (#4489)
- Prevent `string_processing` and `wrap_long_dict_values_in_parens` from removing
  parentheses around long dictionary values (#4377)
- Move `wrap_long_dict_values_in_parens` from the unstable to preview style (#4561)

### Packaging

- Store license identifier inside the `License-Expression` metadata field, see
  [PEP 639](https://peps.python.org/pep-0639/). (#4479)

### Performance

- Speed up the `is_fstring_start` function in Black's tokenizer (#4541)

### Integrations

- If using stdin with `--stdin-filename` set to a force excluded path, stdin won't be
  formatted. (#4539)

## 24.10.0

### Highlights

- Black is now officially tested with Python 3.13 and provides Python 3.13
  mypyc-compiled wheels. (#4436) (#4449)
- Black will issue an error when used with Python 3.12.5, due to an upstream memory
  safety issue in Python 3.12.5 that can cause Black's AST safety checks to fail. Please
  use Python 3.12.6 or Python 3.12.4 instead. (#4447)
- Black no longer supports running with Python 3.8 (#4452)

### Stable style

- Fix crashes involving comments in parenthesised return types or `X | Y` style unions.
  (#4453)
- Fix skipping Jupyter cells with unknown `%%` magic (#4462)

### Preview style

- Fix type annotation spacing between * and more complex type variable tuple (i.e. `def
  fn(*args: *tuple[*Ts, T]) -> None: pass`) (#4440)

### Caching

- Fix bug where the cache was shared between runs with and without `--unstable` (#4466)

### Packaging

- Upgrade version of mypyc used to 1.12 beta (#4450) (#4449)
- `blackd` now requires a newer version of aiohttp. (#4451)

### Output

- Added Python target version information on parse error (#4378)
- Add information about Black version to internal error messages (#4457)

## 24.8.0

### Stable style

- Fix crash when `# fmt: off` is used before a closing parenthesis or bracket. (#4363)

### Packaging

- Packaging metadata updated: docs are explictly linked, the issue tracker is now also
  linked. This improves the PyPI listing for Black. (#4345)

### Parser

- Fix regression where Black failed to parse a multiline f-string containing another
  multiline string (#4339)
- Fix regression where Black failed to parse an escaped single quote inside an f-string
  (#4401)
- Fix bug with Black incorrectly parsing empty lines with a backslash (#4343)
- Fix bugs with Black's tokenizer not handling `\{` inside f-strings very well (#4422)
- Fix incorrect line numbers in the tokenizer for certain tokens within f-strings
  (#4423)

### Performance

- Improve performance when a large directory is listed in `.gitignore` (#4415)

### _Blackd_

- Fix blackd (and all extras installs) for docker container (#4357)

## 24.4.2

This is a bugfix release to fix two regressions in the new f-string parser introduced in
24.4.1.

### Parser

- Fix regression where certain complex f-strings failed to parse (#4332)

### Performance

- Fix bad performance on certain complex string literals (#4331)

## 24.4.1

### Highlights

- Add support for the new Python 3.12 f-string syntax introduced by PEP 701 (#3822)

### Stable style

- Fix crash involving indented dummy functions containing newlines (#4318)

### Parser

- Add support for type parameter defaults, a new syntactic feature added to Python 3.13
  by PEP 696 (#4327)

### Integrations

- Github Action now works even when `git archive` is skipped (#4313)

## 24.4.0

### Stable style

- Fix unwanted crashes caused by AST equivalency check (#4290)

### Preview style

- `if` guards in `case` blocks are now wrapped in parentheses when the line is too long.
  (#4269)
- Stop moving multiline strings to a new line unless inside brackets (#4289)

### Integrations

- Add a new option `use_pyproject` to the GitHub Action `psf/black`. This will read the
  Black version from `pyproject.toml`. (#4294)

## 24.3.0

### Highlights

This release is a milestone: it fixes Black's first CVE security vulnerability. If you
run Black on untrusted input, or if you habitually put thousands of leading tab
characters in your docstrings, you are strongly encouraged to upgrade immediately to fix
[CVE-2024-21503](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-21503).

This release also fixes a bug in Black's AST safety check that allowed Black to make
incorrect changes to certain f-strings that are valid in Python 3.12 and higher.

### Stable style

- Don't move comments along with delimiters, which could cause crashes (#4248)
- Strengthen AST safety check to catch more unsafe changes to strings. Previous versions
  of Black would incorrectly format the contents of certain unusual f-strings containing
  nested strings with the same quote type. Now, Black will crash on such strings until
  support for the new f-string syntax is implemented. (#4270)
- Fix a bug where line-ranges exceeding the last code line would not work as expected
  (#4273)

### Performance

- Fix catastrophic performance on docstrings that contain large numbers of leading tab
  characters. This fixes
  [CVE-2024-21503](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-21503).
  (#4278)

### Documentation

- Note what happens when `--check` is used with `--quiet` (#4236)

## 24.2.0

### Stable style

- Fixed a bug where comments where mistakenly removed along with redundant parentheses
  (#4218)

### Preview style

- Move the `hug_parens_with_braces_and_square_brackets` feature to the unstable style
  due to an outstanding crash and proposed formatting tweaks (#4198)
- Fixed a bug where base expressions caused inconsistent formatting of \*\* in tenary
  expression (#4154)
- Checking for newline before adding one on docstring that is almost at the line limit
  (#4185)
- Remove redundant parentheses in `case` statement `if` guards (#4214).

### Configuration

- Fix issue where _Black_ would ignore input files in the presence of symlinks (#4222)
- _Black_ now ignores `pyproject.toml` that is missing a `tool.black` section when
  discovering project root and configuration. Since _Black_ continues to use version
  control as an indicator of project root, this is expected to primarily change behavior
  for users in a monorepo setup (desirably). If you wish to preserve previous behavior,
  simply add an empty `[tool.black]` to the previously discovered `pyproject.toml`
  (#4204)

### Output

- Black will swallow any `SyntaxWarning`s or `DeprecationWarning`s produced by the `ast`
  module when performing equivalence checks (#4189)

### Integrations

- Add a JSONSchema and provide a validate-pyproject entry-point (#4181)

## 24.1.1

Bugfix release to fix a bug that made Black unusable on certain file systems with strict
limits on path length.

### Preview style

- Consistently add trailing comma on typed parameters (#4164)

### Configuration

- Shorten the length of the name of the cache file to fix crashes on file systems that
  do not support long paths (#4176)

## 24.1.0

### Highlights

This release introduces the new 2024 stable style (#4106), stabilizing the following
changes:

- Add parentheses around `if`-`else` expressions (#2278)
- Dummy class and function implementations consisting only of `...` are formatted more
  compactly (#3796)
- If an assignment statement is too long, we now prefer splitting on the right-hand side
  (#3368)
- Hex codes in Unicode escape sequences are now standardized to lowercase (#2916)
- Allow empty first lines at the beginning of most blocks (#3967, #4061)
- Add parentheses around long type annotations (#3899)
- Enforce newline after module docstrings (#3932, #4028)
- Fix incorrect magic trailing comma handling in return types (#3916)
- Remove blank lines before class docstrings (#3692)
- Wrap multiple context managers in parentheses if combined in a single `with` statement
  (#3489)
- Fix bug in line length calculations for power operations (#3942)
- Add trailing commas to collection literals even if there's a comment after the last
  entry (#3393)
- When using `--skip-magic-trailing-comma` or `-C`, trailing commas are stripped from
  subscript expressions with more than 1 element (#3209)
- Add extra blank lines in stubs in a few cases (#3564, #3862)
- Accept raw strings as docstrings (#3947)
- Split long lines in case blocks (#4024)
- Stop removing spaces from walrus operators within subscripts (#3823)
- Fix incorrect formatting of certain async statements (#3609)
- Allow combining `# fmt: skip` with other comments (#3959)

There are already a few improvements in the `--preview` style, which are slated for the
2025 stable style. Try them out and
[share your feedback](https://github.com/psf/black/issues). In the past, the preview
style has included some features that we were not able to stabilize. This year, we're
adding a separate `--unstable` style for features with known problems. Now, the
`--preview` style only includes features that we actually expect to make it into next
year's stable style.

### Stable style

Several bug fixes were made in features that are moved to the stable style in this
release:

- Fix comment handling when parenthesising conditional expressions (#4134)
- Fix bug where spaces were not added around parenthesized walruses in subscripts,
  unlike other binary operators (#4109)
- Remove empty lines before docstrings in async functions (#4132)
- Address a missing case in the change to allow empty lines at the beginning of all
  blocks, except immediately before a docstring (#4130)
- For stubs, fix logic to enforce empty line after nested classes with bodies (#4141)

### Preview style

- Add `--unstable` style, covering preview features that have known problems that would
  block them from going into the stable style. Also add the `--enable-unstable-feature`
  flag; for example, use
  `--enable-unstable-feature hug_parens_with_braces_and_square_brackets` to apply this
  preview feature throughout 2024, even if a later Black release downgrades the feature
  to unstable (#4096)
- Format module docstrings the same as class and function docstrings (#4095)
- Fix crash when using a walrus in a dictionary (#4155)
- Fix unnecessary parentheses when wrapping long dicts (#4135)
- Stop normalizing spaces before `# fmt: skip` comments (#4146)

### Configuration

- Print warning when configuration in `pyproject.toml` contains an invalid key (#4165)
- Fix symlink handling, properly ignoring symlinks that point outside of root (#4161)
- Fix cache mtime logic that resulted in false positive cache hits (#4128)
- Remove the long-deprecated `--experimental-string-processing` flag. This feature can
  currently be enabled with `--preview --enable-unstable-feature string_processing`.
  (#4096)

### Integrations

- Revert the change to run Black's pre-commit integration only on specific git hooks
  (#3940) for better compatibility with older versions of pre-commit (#4137)

## 23.12.1

### Packaging

- Fixed a bug that included dependencies from the `d` extra by default (#4108)

## 23.12.0

### Highlights

It's almost 2024, which means it's time for a new edition of _Black_'s stable style!
Together with this release, we'll put out an alpha release 24.1a1 showcasing the draft
2024 stable style, which we'll finalize in the January release. Please try it out and
[share your feedback](https://github.com/psf/black/issues/4042).

This release (23.12.0) will still produce the 2023 style. Most but not all of the
changes in `--preview` mode will be in the 2024 stable style.

### Stable style

- Fix bug where `# fmt: off` automatically dedents when used with the `--line-ranges`
  option, even when it is not within the specified line range. (#4084)
- Fix feature detection for parenthesized context managers (#4104)

### Preview style

- Prefer more equal signs before a break when splitting chained assignments (#4010)
- Standalone form feed characters at the module level are no longer removed (#4021)
- Additional cases of immediately nested tuples, lists, and dictionaries are now
  indented less (#4012)
- Allow empty lines at the beginning of all blocks, except immediately before a
  docstring (#4060)
- Fix crash in preview mode when using a short `--line-length` (#4086)
- Keep suites consisting of only an ellipsis on their own lines if they are not
  functions or class definitions (#4066) (#4103)

### Configuration

- `--line-ranges` now skips _Black_'s internal stability check in `--safe` mode. This
  avoids a crash on rare inputs that have many unformatted same-content lines. (#4034)

### Packaging

- Upgrade to mypy 1.7.1 (#4049) (#4069)
- Faster compiled wheels are now available for CPython 3.12 (#4070)

### Integrations

- Enable 3.12 CI (#4035)
- Build docker images in parallel (#4054)
- Build docker images with 3.12 (#4055)

## 23.11.0

### Highlights

- Support formatting ranges of lines with the new `--line-ranges` command-line option
  (#4020)

### Stable style

- Fix crash on formatting bytes strings that look like docstrings (#4003)
- Fix crash when whitespace followed a backslash before newline in a docstring (#4008)
- Fix standalone comments inside complex blocks crashing Black (#4016)
- Fix crash on formatting code like `await (a ** b)` (#3994)
- No longer treat leading f-strings as docstrings. This matches Python's behaviour and
  fixes a crash (#4019)

### Preview style

- Multiline dicts and lists that are the sole argument to a function are now indented
  less (#3964)
- Multiline unpacked dicts and lists as the sole argument to a function are now also
  indented less (#3992)
- In f-string debug expressions, quote types that are visible in the final string are
  now preserved (#4005)
- Fix a bug where long `case` blocks were not split into multiple lines. Also enable
  general trailing comma rules on `case` blocks (#4024)
- Keep requiring two empty lines between module-level docstring and first function or
  class definition (#4028)
- Add support for single-line format skip with other comments on the same line (#3959)

### Configuration

- Consistently apply force exclusion logic before resolving symlinks (#4015)
- Fix a bug in the matching of absolute path names in `--include` (#3976)

### Performance

- Fix mypyc builds on arm64 on macOS (#4017)

### Integrations

- Black's pre-commit integration will now run only on git hooks appropriate for a code
  formatter (#3940)

## 23.10.1

### Highlights

- Maintenance release to get a fix out for GitHub Action edge case (#3957)

### Preview style

- Fix merging implicit multiline strings that have inline comments (#3956)
- Allow empty first line after block open before a comment or compound statement (#3967)

### Packaging

- Change Dockerfile to hatch + compile black (#3965)

### Integrations

- The summary output for GitHub workflows is now suppressible using the `summary`
  parameter. (#3958)
- Fix the action failing when Black check doesn't pass (#3957)

### Documentation

- It is known Windows documentation CI is broken
  https://github.com/psf/black/issues/3968

## 23.10.0

### Stable style

- Fix comments getting removed from inside parenthesized strings (#3909)

### Preview style

- Fix long lines with power operators getting split before the line length (#3942)
- Long type hints are now wrapped in parentheses and properly indented when split across
  multiple lines (#3899)
- Magic trailing commas are now respected in return types. (#3916)
- Require one empty line after module-level docstrings. (#3932)
- Treat raw triple-quoted strings as docstrings (#3947)

### Configuration

- Fix cache versioning logic when `BLACK_CACHE_DIR` is set (#3937)

### Parser

- Fix bug where attributes named `type` were not accepted inside `match` statements
  (#3950)
- Add support for PEP 695 type aliases containing lambdas and other unusual expressions
  (#3949)

### Output

- Black no longer attempts to provide special errors for attempting to format Python 2
  code (#3933)
- Black will more consistently print stacktraces on internal errors in verbose mode
  (#3938)

### Integrations

- The action output displayed in the job summary is now wrapped in Markdown (#3914)

## 23.9.1

Due to various issues, the previous release (23.9.0) did not include compiled mypyc
wheels, which make Black significantly faster. These issues have now been fixed, and
this release should come with compiled wheels once again.

There will be no wheels for Python 3.12 due to a bug in mypyc. We will provide 3.12
wheels in a future release as soon as the mypyc bug is fixed.

### Packaging

- Upgrade to mypy 1.5.1 (#3864)

### Performance

- Store raw tuples instead of NamedTuples in Black's cache, improving performance and
  decreasing the size of the cache (#3877)

## 23.9.0

### Preview style

- More concise formatting for dummy implementations (#3796)
- In stub files, add a blank line between a statement with a body (e.g an
  `if sys.version_info > (3, x):`) and a function definition on the same level (#3862)
- Fix a bug whereby spaces were removed from walrus operators within subscript(#3823)

### Configuration

- Black now applies exclusion and ignore logic before resolving symlinks (#3846)

### Performance

- Avoid importing `IPython` if notebook cells do not contain magics (#3782)
- Improve caching by comparing file hashes as fallback for mtime and size (#3821)

### _Blackd_

- Fix an issue in `blackd` with single character input (#3558)

### Integrations

- Black now has an
  [official pre-commit mirror](https://github.com/psf/black-pre-commit-mirror). Swapping
  `https://github.com/psf/black` to `https://github.com/psf/black-pre-commit-mirror` in
  your `.pre-commit-config.yaml` will make Black about 2x faster (#3828)
- The `.black.env` folder specified by `ENV_PATH` will now be removed on the completion
  of the GitHub Action (#3759)

## 23.7.0

### Highlights

- Runtime support for Python 3.7 has been removed. Formatting 3.7 code will still be
  supported until further notice (#3765)

### Stable style

- Fix a bug where an illegal trailing comma was added to return type annotations using
  PEP 604 unions (#3735)
- Fix several bugs and crashes where comments in stub files were removed or mishandled
  under some circumstances (#3745)
- Fix a crash with multi-line magic comments like `type: ignore` within parentheses
  (#3740)
- Fix error in AST validation when _Black_ removes trailing whitespace in a type comment
  (#3773)

### Preview style

- Implicitly concatenated strings used as function args are no longer wrapped inside
  parentheses (#3640)
- Remove blank lines between a class definition and its docstring (#3692)

### Configuration

- The `--workers` argument to _Black_ can now be specified via the `BLACK_NUM_WORKERS`
  environment variable (#3743)
- `.pytest_cache`, `.ruff_cache` and `.vscode` are now excluded by default (#3691)
- Fix _Black_ not honouring `pyproject.toml` settings when running `--stdin-filename`
  and the `pyproject.toml` found isn't in the current working directory (#3719)
- _Black_ will now error if `exclude` and `extend-exclude` have invalid data types in
  `pyproject.toml`, instead of silently doing the wrong thing (#3764)

### Packaging

- Upgrade mypyc from 0.991 to 1.3 (#3697)
- Remove patching of Click that mitigated errors on Python 3.6 with `LANG=C` (#3768)

### Parser

- Add support for the new PEP 695 syntax in Python 3.12 (#3703)

### Performance

- Speed up _Black_ significantly when the cache is full (#3751)
- Avoid importing `IPython` in a case where we wouldn't need it (#3748)

### Output

- Use aware UTC datetimes internally, avoids deprecation warning on Python 3.12 (#3728)
- Change verbose logging to exactly mirror _Black_'s logic for source discovery (#3749)

### _Blackd_

- The `blackd` argument parser now shows the default values for options in their help
  text (#3712)

### Integrations

- Black is now tested with
  [`PYTHONWARNDEFAULTENCODING = 1`](https://docs.python.org/3/library/io.html#io-encoding-warning)
  (#3763)
- Update GitHub Action to display black output in the job summary (#3688)

### Documentation

- Add a CITATION.cff file to the root of the repository, containing metadata on how to
  cite this software (#3723)
- Update the _classes_ and _exceptions_ documentation in Developer reference to match
  the latest code base (#3755)

## 23.3.0

### Highlights

This release fixes a longstanding confusing behavior in Black's GitHub action, where the
version of the action did not determine the version of Black being run (issue #3382). In
addition, there is a small bug fix around imports and a number of improvements to the
preview style.

Please try out the
[preview style](https://black.readthedocs.io/en/stable/the_black_code_style/future_style.html#preview-style)
with `black --preview` and tell us your feedback. All changes in the preview style are
expected to become part of Black's stable style in January 2024.

### Stable style

- Import lines with `# fmt: skip` and `# fmt: off` no longer have an extra blank line
  added when they are right after another import line (#3610)

### Preview style

- Add trailing commas to collection literals even if there's a comment after the last
  entry (#3393)
- `async def`, `async for`, and `async with` statements are now formatted consistently
  compared to their non-async version. (#3609)
- `with` statements that contain two context managers will be consistently wrapped in
  parentheses (#3589)
- Let string splitters respect [East Asian Width](https://www.unicode.org/reports/tr11/)
  (#3445)
- Now long string literals can be split after East Asian commas and periods (`、` U+3001
  IDEOGRAPHIC COMMA, `。` U+3002 IDEOGRAPHIC FULL STOP, & `，` U+FF0C FULLWIDTH COMMA)
  besides before spaces (#3445)
- For stubs, enforce one blank line after a nested class with a body other than just
  `...` (#3564)
- Improve handling of multiline strings by changing line split behavior (#1879)

### Parser

- Added support for formatting files with invalid type comments (#3594)

### Integrations

- Update GitHub Action to use the version of Black equivalent to action's version if
  version input is not specified (#3543)
- Fix missing Python binary path in autoload script for vim (#3508)

### Documentation

- Document that only the most recent release is supported for security issues;
  vulnerabilities should be reported through Tidelift (#3612)

## 23.1.0

### Highlights

This is the first release of 2023, and following our
[stability policy](https://black.readthedocs.io/en/stable/the_black_code_style/index.html#stability-policy),
it comes with a number of improvements to our stable style, including improvements to
empty line handling, removal of redundant parentheses in several contexts, and output
that highlights implicitly concatenated strings better.

There are also many changes to the preview style; try out `black --preview` and give us
feedback to help us set the stable style for next year.

In addition to style changes, Black now automatically infers the supported Python
versions from your `pyproject.toml` file, removing the need to set Black's target
versions separately.

### Stable style

- Introduce the 2023 stable style, which incorporates most aspects of last year's
  preview style (#3418). Specific changes:
  - Enforce empty lines before classes and functions with sticky leading comments
    (#3302) (22.12.0)
  - Reformat empty and whitespace-only files as either an empty file (if no newline is
    present) or as a single newline character (if a newline is present) (#3348)
    (22.12.0)
  - Implicitly concatenated strings used as function args are now wrapped inside
    parentheses (#3307) (22.12.0)
  - Correctly handle trailing commas that are inside a line's leading non-nested parens
    (#3370) (22.12.0)
  - `--skip-string-normalization` / `-S` now prevents docstring prefixes from being
    normalized as expected (#3168) (since 22.8.0)
  - When using `--skip-magic-trailing-comma` or `-C`, trailing commas are stripped from
    subscript expressions with more than 1 element (#3209) (22.8.0)
  - Implicitly concatenated strings inside a list, set, or tuple are now wrapped inside
    parentheses (#3162) (22.8.0)
  - Fix a string merging/split issue when a comment is present in the middle of
    implicitly concatenated strings on its own line (#3227) (22.8.0)
  - Docstring quotes are no longer moved if it would violate the line length limit
    (#3044, #3430) (22.6.0)
  - Parentheses around return annotations are now managed (#2990) (22.6.0)
  - Remove unnecessary parentheses around awaited objects (#2991) (22.6.0)
  - Remove unnecessary parentheses in `with` statements (#2926) (22.6.0)
  - Remove trailing newlines after code block open (#3035) (22.6.0)
  - Code cell separators `#%%` are now standardised to `# %%` (#2919) (22.3.0)
  - Remove unnecessary parentheses from `except` statements (#2939) (22.3.0)
  - Remove unnecessary parentheses from tuple unpacking in `for` loops (#2945) (22.3.0)
  - Avoid magic-trailing-comma in single-element subscripts (#2942) (22.3.0)
- Fix a crash when a colon line is marked between `# fmt: off` and `# fmt: on` (#3439)

### Preview style

- Format hex codes in unicode escape sequences in string literals (#2916)
- Add parentheses around `if`-`else` expressions (#2278)
- Improve performance on large expressions that contain many strings (#3467)
- Fix a crash in preview style with assert + parenthesized string (#3415)
- Fix crashes in preview style with walrus operators used in function return annotations
  and except clauses (#3423)
- Fix a crash in preview advanced string processing where mixed implicitly concatenated
  regular and f-strings start with an empty span (#3463)
- Fix a crash in preview advanced string processing where a standalone comment is placed
  before a dict's value (#3469)
- Fix an issue where extra empty lines are added when a decorator has `# fmt: skip`
  applied or there is a standalone comment between decorators (#3470)
- Do not put the closing quotes in a docstring on a separate line, even if the line is
  too long (#3430)
- Long values in dict literals are now wrapped in parentheses; correspondingly
  unnecessary parentheses around short values in dict literals are now removed; long
  string lambda values are now wrapped in parentheses (#3440)
- Fix two crashes in preview style involving edge cases with docstrings (#3451)
- Exclude string type annotations from improved string processing; fix crash when the
  return type annotation is stringified and spans across multiple lines (#3462)
- Wrap multiple context managers in parentheses when targeting Python 3.9+ (#3489)
- Fix several crashes in preview style with walrus operators used in `with` statements
  or tuples (#3473)
- Fix an invalid quote escaping bug in f-string expressions where it produced invalid
  code. Implicitly concatenated f-strings with different quotes can now be merged or
  quote-normalized by changing the quotes used in expressions. (#3509)
- Fix crash on `await (yield)` when Black is compiled with mypyc (#3533)

### Configuration

- Black now tries to infer its `--target-version` from the project metadata specified in
  `pyproject.toml` (#3219)

### Packaging

- Upgrade mypyc from `0.971` to `0.991` so mypycified _Black_ can be built on armv7
  (#3380)
  - This also fixes some crashes while using compiled Black with a debug build of
    CPython
- Drop specific support for the `tomli` requirement on 3.11 alpha releases, working
  around a bug that would cause the requirement not to be installed on any non-final
  Python releases (#3448)
- Black now depends on `packaging` version `22.0` or later. This is required for new
  functionality that needs to parse part of the project metadata (#3219)

### Output

- Calling `black --help` multiple times will return the same help contents each time
  (#3516)
- Verbose logging now shows the values of `pyproject.toml` configuration variables
  (#3392)
- Fix false symlink detection messages in verbose output due to using an incorrect
  relative path to the project root (#3385)

### Integrations

- Move 3.11 CI to normal flow now that all dependencies support 3.11 (#3446)
- Docker: Add new `latest_prerelease` tag automation to follow latest black alpha
  release on docker images (#3465)

### Documentation

- Expand `vim-plug` installation instructions to offer more explicit options (#3468)

## 22.12.0

### Preview style

- Enforce empty lines before classes and functions with sticky leading comments (#3302)
- Reformat empty and whitespace-only files as either an empty file (if no newline is
  present) or as a single newline character (if a newline is present) (#3348)
- Implicitly concatenated strings used as function args are now wrapped inside
  parentheses (#3307)
- For assignment statements, prefer splitting the right hand side if the left hand side
  fits on a single line (#3368)
- Correctly handle trailing commas that are inside a line's leading non-nested parens
  (#3370)

### Configuration

- Fix incorrectly applied `.gitignore` rules by considering the `.gitignore` location
  and the relative path to the target file (#3338)
- Fix incorrectly ignoring `.gitignore` presence when more than one source directory is
  specified (#3336)

### Parser

- Parsing support has been added for walruses inside generator expression that are
  passed as function args (for example,
  `any(match := my_re.match(text) for text in texts)`) (#3327).

### Integrations

- Vim plugin: Optionally allow using the system installation of Black via
  `let g:black_use_virtualenv = 0`(#3309)

## 22.10.0

### Highlights

- Runtime support for Python 3.6 has been removed. Formatting 3.6 code will still be
  supported until further notice.

### Stable style

- Fix a crash when `# fmt: on` is used on a different block level than `# fmt: off`
  (#3281)

### Preview style

- Fix a crash when formatting some dicts with parenthesis-wrapped long string keys
  (#3262)

### Configuration

- `.ipynb_checkpoints` directories are now excluded by default (#3293)
- Add `--skip-source-first-line` / `-x` option to ignore the first line of source code
  while formatting (#3299)

### Packaging

- Executables made with PyInstaller will no longer crash when formatting several files
  at once on macOS. Native x86-64 executables for macOS are available once again.
  (#3275)
- Hatchling is now used as the build backend. This will not have any effect for users
  who install Black with its wheels from PyPI. (#3233)
- Faster compiled wheels are now available for CPython 3.11 (#3276)

### _Blackd_

- Windows style (CRLF) newlines will be preserved (#3257).

### Integrations

- Vim plugin: add flag (`g:black_preview`) to enable/disable the preview style (#3246)
- Update GitHub Action to support formatting of Jupyter Notebook files via a `jupyter`
  option (#3282)
- Update GitHub Action to support use of version specifiers (e.g. `<23`) for Black
  version (#3265)

## 22.8.0

### Highlights

- Python 3.11 is now supported, except for _blackd_ as aiohttp does not support 3.11 as
  of publishing (#3234)
- This is the last release that supports running _Black_ on Python 3.6 (formatting 3.6
  code will continue to be supported until further notice)
- Reword the stability policy to say that we may, in rare cases, make changes that
  affect code that was not previously formatted by _Black_ (#3155)

### Stable style

- Fix an infinite loop when using `# fmt: on/off` in the middle of an expression or code
  block (#3158)
- Fix incorrect handling of `# fmt: skip` on colon (`:`) lines (#3148)
- Comments are no longer deleted when a line had spaces removed around power operators
  (#2874)

### Preview style

- Single-character closing docstring quotes are no longer moved to their own line as
  this is invalid. This was a bug introduced in version 22.6.0. (#3166)
- `--skip-string-normalization` / `-S` now prevents docstring prefixes from being
  normalized as expected (#3168)
- When using `--skip-magic-trailing-comma` or `-C`, trailing commas are stripped from
  subscript expressions with more than 1 element (#3209)
- Implicitly concatenated strings inside a list, set, or tuple are now wrapped inside
  parentheses (#3162)
- Fix a string merging/split issue when a comment is present in the middle of implicitly
  concatenated strings on its own line (#3227)

### _Blackd_

- `blackd` now supports enabling the preview style via the `X-Preview` header (#3217)

### Configuration

- Black now uses the presence of debug f-strings to detect target version (#3215)
- Fix misdetection of project root and verbose logging of sources in cases involving
  `--stdin-filename` (#3216)
- Immediate `.gitignore` files in source directories given on the command line are now
  also respected, previously only `.gitignore` files in the project root and
  automatically discovered directories were respected (#3237)

### Documentation

- Recommend using BlackConnect in IntelliJ IDEs (#3150)

### Integrations

- Vim plugin: prefix messages with `Black: ` so it's clear they come from Black (#3194)
- Docker: changed to a /opt/venv installation + added to PATH to be available to
  non-root users (#3202)

### Output

- Change from deprecated `asyncio.get_event_loop()` to create our event loop which
  removes DeprecationWarning (#3164)
- Remove logging from internal `blib2to3` library since it regularly emits error logs
  about failed caching that can and should be ignored (#3193)

### Parser

- Type comments are now included in the AST equivalence check consistently so accidental
  deletion raises an error. Though type comments can't be tracked when running on PyPy
  3.7 due to standard library limitations. (#2874)

### Performance

- Reduce Black's startup time when formatting a single file by 15-30% (#3211)

## 22.6.0

### Style

- Fix unstable formatting involving `#fmt: skip` and `# fmt:skip` comments (notice the
  lack of spaces) (#2970)

### Preview style

- Docstring quotes are no longer moved if it would violate the line length limit (#3044)
- Parentheses around return annotations are now managed (#2990)
- Remove unnecessary parentheses around awaited objects (#2991)
- Remove unnecessary parentheses in `with` statements (#2926)
- Remove trailing newlines after code block open (#3035)

### Integrations

- Add `scripts/migrate-black.py` script to ease introduction of Black to a Git project
  (#3038)

### Output

- Output Python version and implementation as part of `--version` flag (#2997)

### Packaging

- Use `tomli` instead of `tomllib` on Python 3.11 builds where `tomllib` is not
  available (#2987)

### Parser

- [PEP 654](https://peps.python.org/pep-0654/#except) syntax (for example,
  `except *ExceptionGroup:`) is now supported (#3016)
- [PEP 646](https://peps.python.org/pep-0646) syntax (for example,
  `Array[Batch, *Shape]` or `def fn(*args: *T) -> None`) is now supported (#3071)

### Vim Plugin

- Fix `strtobool` function. It didn't parse true/on/false/off. (#3025)

## 22.3.0

### Preview style

- Code cell separators `#%%` are now standardised to `# %%` (#2919)
- Remove unnecessary parentheses from `except` statements (#2939)
- Remove unnecessary parentheses from tuple unpacking in `for` loops (#2945)
- Avoid magic-trailing-comma in single-element subscripts (#2942)

### Configuration

- Do not format `__pypackages__` directories by default (#2836)
- Add support for specifying stable version with `--required-version` (#2832).
- Avoid crashing when the user has no homedir (#2814)
- Avoid crashing when md5 is not available (#2905)
- Fix handling of directory junctions on Windows (#2904)

### Documentation

- Update pylint config documentation (#2931)

### Integrations

- Move test to disable plugin in Vim/Neovim, which speeds up loading (#2896)

### Output

- In verbose mode, log when _Black_ is using user-level config (#2861)

### Packaging

- Fix Black to work with Click 8.1.0 (#2966)
- On Python 3.11 and newer, use the standard library's `tomllib` instead of `tomli`
  (#2903)
- `black-primer`, the deprecated internal devtool, has been removed and copied to a
  [separate repository](https://github.com/cooperlees/black-primer) (#2924)

### Parser

- Black can now parse starred expressions in the target of `for` and `async for`
  statements, e.g `for item in *items_1, *items_2: pass` (#2879).

## 22.1.0

At long last, _Black_ is no longer a beta product! This is the first non-beta release
and the first release covered by our new
[stability policy](https://black.readthedocs.io/en/stable/the_black_code_style/index.html#stability-policy).

### Highlights

- **Remove Python 2 support** (#2740)
- Introduce the `--preview` flag (#2752)

### Style

- Deprecate `--experimental-string-processing` and move the functionality under
  `--preview` (#2789)
- For stubs, one blank line between class attributes and methods is now kept if there's
  at least one pre-existing blank line (#2736)
- Black now normalizes string prefix order (#2297)
- Remove spaces around power operators if both operands are simple (#2726)
- Work around bug that causes unstable formatting in some cases in the presence of the
  magic trailing comma (#2807)
- Use parentheses for attribute access on decimal float and int literals (#2799)
- Don't add whitespace for attribute access on hexadecimal, binary, octal, and complex
  literals (#2799)
- Treat blank lines in stubs the same inside top-level `if` statements (#2820)
- Fix unstable formatting with semicolons and arithmetic expressions (#2817)
- Fix unstable formatting around magic trailing comma (#2572)

### Parser

- Fix mapping cases that contain as-expressions, like `case {"key": 1 | 2 as password}`
  (#2686)
- Fix cases that contain multiple top-level as-expressions, like `case 1 as a, 2 as b`
  (#2716)
- Fix call patterns that contain as-expressions with keyword arguments, like
  `case Foo(bar=baz as quux)` (#2749)
- Tuple unpacking on `return` and `yield` constructs now implies 3.8+ (#2700)
- Unparenthesized tuples on annotated assignments (e.g
  `values: Tuple[int, ...] = 1, 2, 3`) now implies 3.8+ (#2708)
- Fix handling of standalone `match()` or `case()` when there is a trailing newline or a
  comment inside of the parentheses. (#2760)
- `from __future__ import annotations` statement now implies Python 3.7+ (#2690)

### Performance

- Speed-up the new backtracking parser about 4X in general (enabled when
  `--target-version` is set to 3.10 and higher). (#2728)
- _Black_ is now compiled with [mypyc](https://github.com/mypyc/mypyc) for an overall 2x
  speed-up. 64-bit Windows, MacOS, and Linux (not including musl) are supported. (#1009,
  #2431)

### Configuration

- Do not accept bare carriage return line endings in pyproject.toml (#2408)
- Add configuration option (`python-cell-magics`) to format cells with custom magics in
  Jupyter Notebooks (#2744)
- Allow setting custom cache directory on all platforms with environment variable
  `BLACK_CACHE_DIR` (#2739).
- Enable Python 3.10+ by default, without any extra need to specify
  `--target-version=py310`. (#2758)
- Make passing `SRC` or `--code` mandatory and mutually exclusive (#2804)

### Output

- Improve error message for invalid regular expression (#2678)
- Improve error message when parsing fails during AST safety check by embedding the
  underlying SyntaxError (#2693)
- No longer color diff headers white as it's unreadable in light themed terminals
  (#2691)
- Text coloring added in the final statistics (#2712)
- Verbose mode also now describes how a project root was discovered and which paths will
  be formatted. (#2526)

### Packaging

- All upper version bounds on dependencies have been removed (#2718)
- `typing-extensions` is no longer a required dependency in Python 3.10+ (#2772)
- Set `click` lower bound to `8.0.0` (#2791)

### Integrations

- Update GitHub action to support containerized runs (#2748)

### Documentation

- Change protocol in pip installation instructions to `https://` (#2761)
- Change HTML theme to Furo primarily for its responsive design and mobile support
  (#2793)
- Deprecate the `black-primer` tool (#2809)
- Document Python support policy (#2819)

## 21.12b0

### _Black_

- Fix determination of f-string expression spans (#2654)
- Fix bad formatting of error messages about EOF in multi-line statements (#2343)
- Functions and classes in blocks now have more consistent surrounding spacing (#2472)

#### Jupyter Notebook support

- Cell magics are now only processed if they are known Python cell magics. Earlier, all
  cell magics were tokenized, leading to possible indentation errors e.g. with
  `%%writefile`. (#2630)
- Fix assignment to environment variables in Jupyter Notebooks (#2642)

#### Python 3.10 support

- Point users to using `--target-version py310` if we detect 3.10-only syntax (#2668)
- Fix `match` statements with open sequence subjects, like `match a, b:` or
  `match a, *b:` (#2639) (#2659)
- Fix `match`/`case` statements that contain `match`/`case` soft keywords multiple
  times, like `match re.match()` (#2661)
- Fix `case` statements with an inline body (#2665)
- Fix styling of starred expressions inside `match` subject (#2667)
- Fix parser error location on invalid syntax in a `match` statement (#2649)
- Fix Python 3.10 support on platforms without ProcessPoolExecutor (#2631)
- Improve parsing performance on code that uses `match` under `--target-version py310`
  up to ~50% (#2670)

### Packaging

- Remove dependency on `regex` (#2644) (#2663)

## 21.11b1

### _Black_

- Bumped regex version minimum to 2021.4.4 to fix Pattern class usage (#2621)

## 21.11b0

### _Black_

- Warn about Python 2 deprecation in more cases by improving Python 2 only syntax
  detection (#2592)
- Add experimental PyPy support (#2559)
- Add partial support for the match statement. As it's experimental, it's only enabled
  when `--target-version py310` is explicitly specified (#2586)
- Add support for parenthesized with (#2586)
- Declare support for Python 3.10 for running Black (#2562)

### Integrations

- Fixed vim plugin with Python 3.10 by removing deprecated distutils import (#2610)
- The vim plugin now parses `skip_magic_trailing_comma` from pyproject.toml (#2613)

## 21.10b0

### _Black_

- Document stability policy, that will apply for non-beta releases (#2529)
- Add new `--workers` parameter (#2514)
- Fixed feature detection for positional-only arguments in lambdas (#2532)
- Bumped typed-ast version minimum to 1.4.3 for 3.10 compatibility (#2519)
- Fixed a Python 3.10 compatibility issue where the loop argument was still being passed
  even though it has been removed (#2580)
- Deprecate Python 2 formatting support (#2523)

### _Blackd_

- Remove dependency on aiohttp-cors (#2500)
- Bump required aiohttp version to 3.7.4 (#2509)

### _Black-Primer_

- Add primer support for --projects (#2555)
- Print primer summary after individual failures (#2570)

### Integrations

- Allow to pass `target_version` in the vim plugin (#1319)
- Install build tools in docker file and use multi-stage build to keep the image size
  down (#2582)

## 21.9b0

### Packaging

- Fix missing modules in self-contained binaries (#2466)
- Fix missing toml extra used during installation (#2475)

## 21.8b0

### _Black_

- Add support for formatting Jupyter Notebook files (#2357)
- Move from `appdirs` dependency to `platformdirs` (#2375)
- Present a more user-friendly error if .gitignore is invalid (#2414)
- The failsafe for accidentally added backslashes in f-string expressions has been
  hardened to handle more edge cases during quote normalization (#2437)
- Avoid changing a function return type annotation's type to a tuple by adding a
  trailing comma (#2384)
- Parsing support has been added for unparenthesized walruses in set literals, set
  comprehensions, and indices (#2447).
- Pin `setuptools-scm` build-time dependency version (#2457)
- Exclude typing-extensions version 3.10.0.1 due to it being broken on Python 3.10
  (#2460)

### _Blackd_

- Replace sys.exit(-1) with raise ImportError as it plays more nicely with tools that
  scan installed packages (#2440)

### Integrations

- The provided pre-commit hooks no longer specify `language_version` to avoid overriding
  `default_language_version` (#2430)

## 21.7b0

### _Black_

- Configuration files using TOML features higher than spec v0.5.0 are now supported
  (#2301)
- Add primer support and test for code piped into black via STDIN (#2315)
- Fix internal error when `FORCE_OPTIONAL_PARENTHESES` feature is enabled (#2332)
- Accept empty stdin (#2346)
- Provide a more useful error when parsing fails during AST safety checks (#2304)

### Docker

- Add new `latest_release` tag automation to follow latest black release on docker
  images (#2374)

### Integrations

- The vim plugin now searches upwards from the directory containing the current buffer
  instead of the current working directory for pyproject.toml. (#1871)
- The vim plugin now reads the correct string normalization option in pyproject.toml
  (#1869)
- The vim plugin no longer crashes Black when there's boolean values in pyproject.toml
  (#1869)

## 21.6b0

### _Black_

- Fix failure caused by `fmt: skip` and indentation (#2281)
- Account for += assignment when deciding whether to split string (#2312)
- Correct max string length calculation when there are string operators (#2292)
- Fixed option usage when using the `--code` flag (#2259)
- Do not call `uvloop.install()` when _Black_ is used as a library (#2303)
- Added `--required-version` option to require a specific version to be running (#2300)
- Fix incorrect custom breakpoint indices when string group contains fake f-strings
  (#2311)
- Fix regression where `R` prefixes would be lowercased for docstrings (#2285)
- Fix handling of named escapes (`\N{...}`) when `--experimental-string-processing` is
  used (#2319)

### Integrations

- The official Black action now supports choosing what version to use, and supports the
  major 3 OSes. (#1940)

## 21.5b2

### _Black_

- A space is no longer inserted into empty docstrings (#2249)
- Fix handling of .gitignore files containing non-ASCII characters on Windows (#2229)
- Respect `.gitignore` files in all levels, not only `root/.gitignore` file (apply
  `.gitignore` rules like `git` does) (#2225)
- Restored compatibility with Click 8.0 on Python 3.6 when LANG=C used (#2227)
- Add extra uvloop install + import support if in python env (#2258)
- Fix --experimental-string-processing crash when matching parens are not found (#2283)
- Make sure to split lines that start with a string operator (#2286)
- Fix regular expression that black uses to identify f-expressions (#2287)

### _Blackd_

- Add a lower bound for the `aiohttp-cors` dependency. Only 0.4.0 or higher is
  supported. (#2231)

### Packaging

- Release self-contained x86_64 MacOS binaries as part of the GitHub release pipeline
  (#2198)
- Always build binaries with the latest available Python (#2260)

### Documentation

- Add discussion of magic comments to FAQ page (#2272)
- `--experimental-string-processing` will be enabled by default in the future (#2273)
- Fix typos discovered by codespell (#2228)
- Fix Vim plugin installation instructions. (#2235)
- Add new Frequently Asked Questions page (#2247)
- Fix encoding + symlink issues preventing proper build on Windows (#2262)

## 21.5b1

### _Black_

- Refactor `src/black/__init__.py` into many files (#2206)

### Documentation

- Replaced all remaining references to the
  [`master`](https://github.com/psf/black/tree/main) branch with the
  [`main`](https://github.com/psf/black/tree/main) branch. Some additional changes in
  the source code were also made. (#2210)
- Significantly reorganized the documentation to make much more sense. Check them out by
  heading over to [the stable docs on RTD](https://black.readthedocs.io/en/stable/).
  (#2174)

## 21.5b0

### _Black_

- Set `--pyi` mode if `--stdin-filename` ends in `.pyi` (#2169)
- Stop detecting target version as Python 3.9+ with pre-PEP-614 decorators that are
  being called but with no arguments (#2182)

### _Black-Primer_

- Add `--no-diff` to black-primer to suppress formatting changes (#2187)

## 21.4b2

### _Black_

- Fix crash if the user configuration directory is inaccessible. (#2158)

- Clarify
  [circumstances](https://github.com/psf/black/blob/master/docs/the_black_code_style.md#pragmatism)
  in which _Black_ may change the AST (#2159)

- Allow `.gitignore` rules to be overridden by specifying `exclude` in `pyproject.toml`
  or on the command line. (#2170)

### _Packaging_

- Install `primer.json` (used by `black-primer` by default) with black. (#2154)

## 21.4b1

### _Black_

- Fix crash on docstrings ending with "\\ ". (#2142)

- Fix crash when atypical whitespace is cleaned out of dostrings (#2120)

- Reflect the `--skip-magic-trailing-comma` and `--experimental-string-processing` flags
  in the name of the cache file. Without this fix, changes in these flags would not take
  effect if the cache had already been populated. (#2131)

- Don't remove necessary parentheses from assignment expression containing assert /
  return statements. (#2143)

### _Packaging_

- Bump pathspec to >= 0.8.1 to solve invalid .gitignore exclusion handling

## 21.4b0

### _Black_

- Fixed a rare but annoying formatting instability created by the combination of
  optional trailing commas inserted by `Black` and optional parentheses looking at
  pre-existing "magic" trailing commas. This fixes issue #1629 and all of its many many
  duplicates. (#2126)

- `Black` now processes one-line docstrings by stripping leading and trailing spaces,
  and adding a padding space when needed to break up """". (#1740)

- `Black` now cleans up leading non-breaking spaces in comments (#2092)

- `Black` now respects `--skip-string-normalization` when normalizing multiline
  docstring quotes (#1637)

- `Black` no longer removes all empty lines between non-function code and decorators
  when formatting typing stubs. Now `Black` enforces a single empty line. (#1646)

- `Black` no longer adds an incorrect space after a parenthesized assignment expression
  in if/while statements (#1655)

- Added `--skip-magic-trailing-comma` / `-C` to avoid using trailing commas as a reason
  to split lines (#1824)

- fixed a crash when PWD=/ on POSIX (#1631)

- fixed "I/O operation on closed file" when using --diff (#1664)

- Prevent coloured diff output being interleaved with multiple files (#1673)

- Added support for PEP 614 relaxed decorator syntax on python 3.9 (#1711)

- Added parsing support for unparenthesized tuples and yield expressions in annotated
  assignments (#1835)

- added `--extend-exclude` argument (PR #2005)

- speed up caching by avoiding pathlib (#1950)

- `--diff` correctly indicates when a file doesn't end in a newline (#1662)

- Added `--stdin-filename` argument to allow stdin to respect `--force-exclude` rules
  (#1780)

- Lines ending with `fmt: skip` will now be not formatted (#1800)

- PR #2053: Black no longer relies on typed-ast for Python 3.8 and higher

- PR #2053: Python 2 support is now optional, install with
  `python3 -m pip install black[python2]` to maintain support.

- Exclude `venv` directory by default (#1683)

- Fixed "Black produced code that is not equivalent to the source" when formatting
  Python 2 docstrings (#2037)

### _Packaging_

- Self-contained native _Black_ binaries are now provided for releases via GitHub
  Releases (#1743)

## 20.8b1

### _Packaging_

- explicitly depend on Click 7.1.2 or newer as `Black` no longer works with versions
  older than 7.0

## 20.8b0

### _Black_

- re-implemented support for explicit trailing commas: now it works consistently within
  any bracket pair, including nested structures (#1288 and duplicates)

- `Black` now reindents docstrings when reindenting code around it (#1053)

- `Black` now shows colored diffs (#1266)

- `Black` is now packaged using 'py3' tagged wheels (#1388)

- `Black` now supports Python 3.8 code, e.g. star expressions in return statements
  (#1121)

- `Black` no longer normalizes capital R-string prefixes as those have a
  community-accepted meaning (#1244)

- `Black` now uses exit code 2 when specified configuration file doesn't exit (#1361)

- `Black` now works on AWS Lambda (#1141)

- added `--force-exclude` argument (#1032)

- removed deprecated `--py36` option (#1236)

- fixed `--diff` output when EOF is encountered (#526)

- fixed `# fmt: off` handling around decorators (#560)

- fixed unstable formatting with some `# type: ignore` comments (#1113)

- fixed invalid removal on organizing brackets followed by indexing (#1575)

- introduced `black-primer`, a CI tool that allows us to run regression tests against
  existing open source users of Black (#1402)

- introduced property-based fuzzing to our test suite based on Hypothesis and
  Hypothersmith (#1566)

- implemented experimental and disabled by default long string rewrapping (#1132),
  hidden under a `--experimental-string-processing` flag while it's being worked on;
  this is an undocumented and unsupported feature, you lose Internet points for
  depending on it (#1609)

### Vim plugin

- prefer virtualenv packages over global packages (#1383)

## 19.10b0

- added support for PEP 572 assignment expressions (#711)

- added support for PEP 570 positional-only arguments (#943)

- added support for async generators (#593)

- added support for pre-splitting collections by putting an explicit trailing comma
  inside (#826)

- added `black -c` as a way to format code passed from the command line (#761)

- --safe now works with Python 2 code (#840)

- fixed grammar selection for Python 2-specific code (#765)

- fixed feature detection for trailing commas in function definitions and call sites
  (#763)

- `# fmt: off`/`# fmt: on` comment pairs placed multiple times within the same block of
  code now behave correctly (#1005)

- _Black_ no longer crashes on Windows machines with more than 61 cores (#838)

- _Black_ no longer crashes on standalone comments prepended with a backslash (#767)

- _Black_ no longer crashes on `from` ... `import` blocks with comments (#829)

- _Black_ no longer crashes on Python 3.7 on some platform configurations (#494)

- _Black_ no longer fails on comments in from-imports (#671)

- _Black_ no longer fails when the file starts with a backslash (#922)

- _Black_ no longer merges regular comments with type comments (#1027)

- _Black_ no longer splits long lines that contain type comments (#997)

- removed unnecessary parentheses around `yield` expressions (#834)

- added parentheses around long tuples in unpacking assignments (#832)

- added parentheses around complex powers when they are prefixed by a unary operator
  (#646)

- fixed bug that led _Black_ format some code with a line length target of 1 (#762)

- _Black_ no longer introduces quotes in f-string subexpressions on string boundaries
  (#863)

- if _Black_ puts parenthesis around a single expression, it moves comments to the
  wrapped expression instead of after the brackets (#872)

- `blackd` now returns the version of _Black_ in the response headers (#1013)

- `blackd` can now output the diff of formats on source code when the `X-Diff` header is
  provided (#969)

## 19.3b0

- new option `--target-version` to control which Python versions _Black_-formatted code
  should target (#618)

- deprecated `--py36` (use `--target-version=py36` instead) (#724)

- _Black_ no longer normalizes numeric literals to include `_` separators (#696)

- long `del` statements are now split into multiple lines (#698)

- type comments are no longer mangled in function signatures

- improved performance of formatting deeply nested data structures (#509)

- _Black_ now properly formats multiple files in parallel on Windows (#632)

- _Black_ now creates cache files atomically which allows it to be used in parallel
  pipelines (like `xargs -P8`) (#673)

- _Black_ now correctly indents comments in files that were previously formatted with
  tabs (#262)

- `blackd` now supports CORS (#622)

## 18.9b0

- numeric literals are now formatted by _Black_ (#452, #461, #464, #469):
  - numeric literals are normalized to include `_` separators on Python 3.6+ code

  - added `--skip-numeric-underscore-normalization` to disable the above behavior and
    leave numeric underscores as they were in the input

  - code with `_` in numeric literals is recognized as Python 3.6+

  - most letters in numeric literals are lowercased (e.g., in `1e10`, `0x01`)

  - hexadecimal digits are always uppercased (e.g. `0xBADC0DE`)

- added `blackd`, see
  [its documentation](https://github.com/psf/black/blob/18.9b0/README.md#blackd) for
  more info (#349)

- adjacent string literals are now correctly split into multiple lines (#463)

- trailing comma is now added to single imports that don't fit on a line (#250)

- cache is now populated when `--check` is successful for a file which speeds up
  consecutive checks of properly formatted unmodified files (#448)

- whitespace at the beginning of the file is now removed (#399)

- fixed mangling [pweave](http://mpastell.com/pweave/) and
  [Spyder IDE](https://www.spyder-ide.org/) special comments (#532)

- fixed unstable formatting when unpacking big tuples (#267)

- fixed parsing of `__future__` imports with renames (#389)

- fixed scope of `# fmt: off` when directly preceding `yield` and other nodes (#385)

- fixed formatting of lambda expressions with default arguments (#468)

- fixed `async for` statements: _Black_ no longer breaks them into separate lines (#372)

- note: the Vim plugin stopped registering `,=` as a default chord as it turned out to
  be a bad idea (#415)

## 18.6b4

- hotfix: don't freeze when multiple comments directly precede `# fmt: off` (#371)

## 18.6b3

- typing stub files (`.pyi`) now have blank lines added after constants (#340)

- `# fmt: off` and `# fmt: on` are now much more dependable:
  - they now work also within bracket pairs (#329)

  - they now correctly work across function/class boundaries (#335)

  - they now work when an indentation block starts with empty lines or misaligned
    comments (#334)

- made Click not fail on invalid environments; note that Click is right but the
  likelihood we'll need to access non-ASCII file paths when dealing with Python source
  code is low (#277)

- fixed improper formatting of f-strings with quotes inside interpolated expressions
  (#322)

- fixed unnecessary slowdown when long list literals where found in a file

- fixed unnecessary slowdown on AST nodes with very many siblings

- fixed cannibalizing backslashes during string normalization

- fixed a crash due to symbolic links pointing outside of the project directory (#338)

## 18.6b2

- added `--config` (#65)

- added `-h` equivalent to `--help` (#316)

- fixed improper unmodified file caching when `-S` was used

- fixed extra space in string unpacking (#305)

- fixed formatting of empty triple quoted strings (#313)

- fixed unnecessary slowdown in comment placement calculation on lines without comments

## 18.6b1

- hotfix: don't output human-facing information on stdout (#299)

- hotfix: don't output cake emoji on non-zero return code (#300)

## 18.6b0

- added `--include` and `--exclude` (#270)

- added `--skip-string-normalization` (#118)

- added `--verbose` (#283)

- the header output in `--diff` now actually conforms to the unified diff spec

- fixed long trivial assignments being wrapped in unnecessary parentheses (#273)

- fixed unnecessary parentheses when a line contained multiline strings (#232)

- fixed stdin handling not working correctly if an old version of Click was used (#276)

- _Black_ now preserves line endings when formatting a file in place (#258)

## 18.5b1

- added `--pyi` (#249)

- added `--py36` (#249)

- Python grammar pickle caches are stored with the formatting caches, making _Black_
  work in environments where site-packages is not user-writable (#192)

- _Black_ now enforces a PEP 257 empty line after a class-level docstring (and/or
  fields) and the first method

- fixed invalid code produced when standalone comments were present in a trailer that
  was omitted from line splitting on a large expression (#237)

- fixed optional parentheses being removed within `# fmt: off` sections (#224)

- fixed invalid code produced when stars in very long imports were incorrectly wrapped
  in optional parentheses (#234)

- fixed unstable formatting when inline comments were moved around in a trailer that was
  omitted from line splitting on a large expression (#238)

- fixed extra empty line between a class declaration and the first method if no class
  docstring or fields are present (#219)

- fixed extra empty line between a function signature and an inner function or inner
  class (#196)

## 18.5b0

- call chains are now formatted according to the
  [fluent interfaces](https://en.wikipedia.org/wiki/Fluent_interface) style (#67)

- data structure literals (tuples, lists, dictionaries, and sets) are now also always
  exploded like imports when they don't fit in a single line (#152)

- slices are now formatted according to PEP 8 (#178)

- parentheses are now also managed automatically on the right-hand side of assignments
  and return statements (#140)

- math operators now use their respective priorities for delimiting multiline
  expressions (#148)

- optional parentheses are now omitted on expressions that start or end with a bracket
  and only contain a single operator (#177)

- empty parentheses in a class definition are now removed (#145, #180)

- string prefixes are now standardized to lowercase and `u` is removed on Python 3.6+
  only code and Python 2.7+ code with the `unicode_literals` future import (#188, #198,
  #199)

- typing stub files (`.pyi`) are now formatted in a style that is consistent with PEP
  484 (#207, #210)

- progress when reformatting many files is now reported incrementally

- fixed trailers (content with brackets) being unnecessarily exploded into their own
  lines after a dedented closing bracket (#119)

- fixed an invalid trailing comma sometimes left in imports (#185)

- fixed non-deterministic formatting when multiple pairs of removable parentheses were
  used (#183)

- fixed multiline strings being unnecessarily wrapped in optional parentheses in long
  assignments (#215)

- fixed not splitting long from-imports with only a single name

- fixed Python 3.6+ file discovery by also looking at function calls with unpacking.
  This fixed non-deterministic formatting if trailing commas where used both in function
  signatures with stars and function calls with stars but the former would be
  reformatted to a single line.

- fixed crash on dealing with optional parentheses (#193)

- fixed "is", "is not", "in", and "not in" not considered operators for splitting
  purposes

- fixed crash when dead symlinks where encountered

## 18.4a4

- don't populate the cache on `--check` (#175)

## 18.4a3

- added a "cache"; files already reformatted that haven't changed on disk won't be
  reformatted again (#109)

- `--check` and `--diff` are no longer mutually exclusive (#149)

- generalized star expression handling, including double stars; this fixes
  multiplication making expressions "unsafe" for trailing commas (#132)

- _Black_ no longer enforces putting empty lines behind control flow statements (#90)

- _Black_ now splits imports like "Mode 3 + trailing comma" of isort (#127)

- fixed comment indentation when a standalone comment closes a block (#16, #32)

- fixed standalone comments receiving extra empty lines if immediately preceding a
  class, def, or decorator (#56, #154)

- fixed `--diff` not showing entire path (#130)

- fixed parsing of complex expressions after star and double stars in function calls
  (#2)

- fixed invalid splitting on comma in lambda arguments (#133)

- fixed missing splits of ternary expressions (#141)

## 18.4a2

- fixed parsing of unaligned standalone comments (#99, #112)

- fixed placement of dictionary unpacking inside dictionary literals (#111)

- Vim plugin now works on Windows, too

- fixed unstable formatting when encountering unnecessarily escaped quotes in a string
  (#120)

## 18.4a1

- added `--quiet` (#78)

- added automatic parentheses management (#4)

- added [pre-commit](https://pre-commit.com) integration (#103, #104)

- fixed reporting on `--check` with multiple files (#101, #102)

- fixed removing backslash escapes from raw strings (#100, #105)

## 18.4a0

- added `--diff` (#87)

- add line breaks before all delimiters, except in cases like commas, to better comply
  with PEP 8 (#73)

- standardize string literals to use double quotes (almost) everywhere (#75)

- fixed handling of standalone comments within nested bracketed expressions; _Black_
  will no longer produce super long lines or put all standalone comments at the end of
  the expression (#22)

- fixed 18.3a4 regression: don't crash and burn on empty lines with trailing whitespace
  (#80)

- fixed 18.3a4 regression: `# yapf: disable` usage as trailing comment would cause
  _Black_ to not emit the rest of the file (#95)

- when CTRL+C is pressed while formatting many files, _Black_ no longer freaks out with
  a flurry of asyncio-related exceptions

- only allow up to two empty lines on module level and only single empty lines within
  functions (#74)

## 18.3a4

- `# fmt: off` and `# fmt: on` are implemented (#5)

- automatic detection of deprecated Python 2 forms of print statements and exec
  statements in the formatted file (#49)

- use proper spaces for complex expressions in default values of typed function
  arguments (#60)

- only return exit code 1 when --check is used (#50)

- don't remove single trailing commas from square bracket indexing (#59)

- don't omit whitespace if the previous factor leaf wasn't a math operator (#55)

- omit extra space in kwarg unpacking if it's the first argument (#46)

- omit extra space in
  [Sphinx auto-attribute comments](http://www.sphinx-doc.org/en/stable/ext/autodoc.html#directive-autoattribute)
  (#68)

## 18.3a3

- don't remove single empty lines outside of bracketed expressions (#19)

- added ability to pipe formatting from stdin to stdin (#25)

- restored ability to format code with legacy usage of `async` as a name (#20, #42)

- even better handling of numpy-style array indexing (#33, again)

## 18.3a2

- changed positioning of binary operators to occur at beginning of lines instead of at
  the end, following
  [a recent change to PEP 8](https://github.com/python/peps/commit/c59c4376ad233a62ca4b3a6060c81368bd21e85b)
  (#21)

- ignore empty bracket pairs while splitting. This avoids very weirdly looking
  formattings (#34, #35)

- remove a trailing comma if there is a single argument to a call

- if top level functions were separated by a comment, don't put four empty lines after
  the upper function

- fixed unstable formatting of newlines with imports

- fixed unintentional folding of post scriptum standalone comments into last statement
  if it was a simple statement (#18, #28)

- fixed missing space in numpy-style array indexing (#33)

- fixed spurious space after star-based unary expressions (#31)

## 18.3a1

- added `--check`

- only put trailing commas in function signatures and calls if it's safe to do so. If
  the file is Python 3.6+ it's always safe, otherwise only safe if there are no `*args`
  or `**kwargs` used in the signature or call. (#8)

- fixed invalid spacing of dots in relative imports (#6, #13)

- fixed invalid splitting after comma on unpacked variables in for-loops (#23)

- fixed spurious space in parenthesized set expressions (#7)

- fixed spurious space after opening parentheses and in default arguments (#14, #17)

- fixed spurious space after unary operators when the operand was a complex expression
  (#15)

## 18.3a0

- first published version, Happy 🍰 Day 2018!

- alpha quality

- date-versioned (see: <https://calver.org/>)
