## Change Log

### 19.10b0

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

### 19.3b0

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

### 18.9b0

- numeric literals are now formatted by _Black_ (#452, #461, #464, #469):

  - numeric literals are normalized to include `_` separators on Python 3.6+ code

  - added `--skip-numeric-underscore-normalization` to disable the above behavior and
    leave numeric underscores as they were in the input

  - code with `_` in numeric literals is recognized as Python 3.6+

  - most letters in numeric literals are lowercased (e.g., in `1e10`, `0x01`)

  - hexadecimal digits are always uppercased (e.g. `0xBADC0DE`)

- added `blackd`, see [its documentation](#blackd) for more info (#349)

- adjacent string literals are now correctly split into multiple lines (#463)

- trailing comma is now added to single imports that don't fit on a line (#250)

- cache is now populated when `--check` is successful for a file which speeds up
  consecutive checks of properly formatted unmodified files (#448)

- whitespace at the beginning of the file is now removed (#399)

- fixed mangling [pweave](http://mpastell.com/pweave/) and
  [Spyder IDE](https://pythonhosted.org/spyder/) special comments (#532)

- fixed unstable formatting when unpacking big tuples (#267)

- fixed parsing of `__future__` imports with renames (#389)

- fixed scope of `# fmt: off` when directly preceding `yield` and other nodes (#385)

- fixed formatting of lambda expressions with default arguments (#468)

- fixed `async for` statements: _Black_ no longer breaks them into separate lines (#372)

- note: the Vim plugin stopped registering `,=` as a default chord as it turned out to
  be a bad idea (#415)

### 18.6b4

- hotfix: don't freeze when multiple comments directly precede `# fmt: off` (#371)

### 18.6b3

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

### 18.6b2

- added `--config` (#65)

- added `-h` equivalent to `--help` (#316)

- fixed improper unmodified file caching when `-S` was used

- fixed extra space in string unpacking (#305)

- fixed formatting of empty triple quoted strings (#313)

- fixed unnecessary slowdown in comment placement calculation on lines without comments

### 18.6b1

- hotfix: don't output human-facing information on stdout (#299)

- hotfix: don't output cake emoji on non-zero return code (#300)

### 18.6b0

- added `--include` and `--exclude` (#270)

- added `--skip-string-normalization` (#118)

- added `--verbose` (#283)

- the header output in `--diff` now actually conforms to the unified diff spec

- fixed long trivial assignments being wrapped in unnecessary parentheses (#273)

- fixed unnecessary parentheses when a line contained multiline strings (#232)

- fixed stdin handling not working correctly if an old version of Click was used (#276)

- _Black_ now preserves line endings when formatting a file in place (#258)

### 18.5b1

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

### 18.5b0

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

### 18.4a4

- don't populate the cache on `--check` (#175)

### 18.4a3

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

### 18.4a2

- fixed parsing of unaligned standalone comments (#99, #112)

- fixed placement of dictionary unpacking inside dictionary literals (#111)

- Vim plugin now works on Windows, too

- fixed unstable formatting when encountering unnecessarily escaped quotes in a string
  (#120)

### 18.4a1

- added `--quiet` (#78)

- added automatic parentheses management (#4)

- added [pre-commit](https://pre-commit.com) integration (#103, #104)

- fixed reporting on `--check` with multiple files (#101, #102)

- fixed removing backslash escapes from raw strings (#100, #105)

### 18.4a0

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

### 18.3a4

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

### 18.3a3

- don't remove single empty lines outside of bracketed expressions (#19)

- added ability to pipe formatting from stdin to stdin (#25)

- restored ability to format code with legacy usage of `async` as a name (#20, #42)

- even better handling of numpy-style array indexing (#33, again)

### 18.3a2

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

### 18.3a1

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

### 18.3a0

- first published version, Happy 🍰 Day 2018!

- alpha quality

- date-versioned (see: https://calver.org/)
