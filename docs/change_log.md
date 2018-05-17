## Change Log

### 18.5a0 (unreleased)

* call chains are now formatted according to the [fluent interfaces](https://en.wikipedia.org/wiki/Fluent_interface) style (#67)

* slices are now formatted according to PEP 8 (#178)

* parentheses are now also managed automatically on the right-hand side
  of assignments and return statements (#140)

* math operators now use their respective priorities for delimiting multiline
  expressions (#148)

* optional parentheses are now omitted on expressions that start or end
  with a bracket and only contain a single operator (#177)

* empty parentheses in a class definition are now removed (#145, #180)

* string prefixes are now standardized to lowercase and `u` is removed
  on Python 3.6+ only code and Python 2.7+ code with the `unicode_literals`
  future import (#188, #198, #199)

* typing stub files (`.pyi`) are now formatted in a style that is consistent
  with PEP 484 (#207, #210)

* progress when reformatting many files is now reported incrementally

* fixed trailers (content with brackets) being unnecessarily exploded
  into their own lines after a dedented closing bracket (#119)

* fixed an invalid trailing comma sometimes left in imports (#185)

* fixed non-deterministic formatting when multiple pairs of removable parentheses
  were used (#183)

* fixed multiline strings being unnecessarily wrapped in optional
  parentheses in long assignments (#215)

* fixed not splitting long from-imports with only a single name

* fixed Python 3.6+ file discovery by also looking at function calls with
  unpacking. This fixed non-deterministic formatting if trailing commas
  where used both in function signatures with stars and function calls
  with stars but the former would be reformatted to a single line.

* fixed crash on dealing with optional parentheses (#193)

* fixed "is", "is not", "in", and "not in" not considered operators for
  splitting purposes

* fixed crash when dead symlinks where encountered


### 18.4a4

* don't populate the cache on `--check` (#175)


### 18.4a3

* added a "cache"; files already reformatted that haven't changed on disk
  won't be reformatted again (#109)

* `--check` and `--diff` are no longer mutually exclusive (#149)

* generalized star expression handling, including double stars; this
  fixes multiplication making expressions "unsafe" for trailing commas (#132)

* Black no longer enforces putting empty lines behind control flow statements
  (#90)

* Black now splits imports like "Mode 3 + trailing comma" of isort (#127)

* fixed comment indentation when a standalone comment closes a block (#16, #32)

* fixed standalone comments receiving extra empty lines if immediately preceding
  a class, def, or decorator (#56, #154)

* fixed `--diff` not showing entire path (#130)

* fixed parsing of complex expressions after star and double stars in
  function calls (#2)

* fixed invalid splitting on comma in lambda arguments (#133)

* fixed missing splits of ternary expressions (#141)


### 18.4a2

* fixed parsing of unaligned standalone comments (#99, #112)

* fixed placement of dictionary unpacking inside dictionary literals (#111)

* Vim plugin now works on Windows, too

* fixed unstable formatting when encountering unnecessarily escaped quotes
  in a string (#120)


### 18.4a1

* added `--quiet` (#78)

* added automatic parentheses management (#4)

* added [pre-commit](https://pre-commit.com) integration (#103, #104)

* fixed reporting on `--check` with multiple files (#101, #102)

* fixed removing backslash escapes from raw strings (#100, #105)


### 18.4a0

* added `--diff` (#87)

* add line breaks before all delimiters, except in cases like commas, to
  better comply with PEP 8 (#73)

* standardize string literals to use double quotes (almost) everywhere
  (#75)

* fixed handling of standalone comments within nested bracketed
  expressions; Black will no longer produce super long lines or put all
  standalone comments at the end of the expression (#22)

* fixed 18.3a4 regression: don't crash and burn on empty lines with
  trailing whitespace (#80)

* fixed 18.3a4 regression: `# yapf: disable` usage as trailing comment
  would cause Black to not emit the rest of the file (#95)

* when CTRL+C is pressed while formatting many files, Black no longer
  freaks out with a flurry of asyncio-related exceptions

* only allow up to two empty lines on module level and only single empty
  lines within functions (#74)


### 18.3a4

* `# fmt: off` and `# fmt: on` are implemented (#5)

* automatic detection of deprecated Python 2 forms of print statements
  and exec statements in the formatted file (#49)

* use proper spaces for complex expressions in default values of typed
  function arguments (#60)

* only return exit code 1 when --check is used (#50)

* don't remove single trailing commas from square bracket indexing
  (#59)

* don't omit whitespace if the previous factor leaf wasn't a math
  operator (#55)

* omit extra space in kwarg unpacking if it's the first argument (#46)

* omit extra space in [Sphinx auto-attribute comments](http://www.sphinx-doc.org/en/stable/ext/autodoc.html#directive-autoattribute)
  (#68)


### 18.3a3

* don't remove single empty lines outside of bracketed expressions
  (#19)

* added ability to pipe formatting from stdin to stdin (#25)

* restored ability to format code with legacy usage of `async` as
  a name (#20, #42)

* even better handling of numpy-style array indexing (#33, again)


### 18.3a2

* changed positioning of binary operators to occur at beginning of lines
  instead of at the end, following [a recent change to PEP8](https://github.com/python/peps/commit/c59c4376ad233a62ca4b3a6060c81368bd21e85b)
  (#21)

* ignore empty bracket pairs while splitting. This avoids very weirdly
  looking formattings (#34, #35)

* remove a trailing comma if there is a single argument to a call

* if top level functions were separated by a comment, don't put four
  empty lines after the upper function

* fixed unstable formatting of newlines with imports

* fixed unintentional folding of post scriptum standalone comments
  into last statement if it was a simple statement (#18, #28)

* fixed missing space in numpy-style array indexing (#33)

* fixed spurious space after star-based unary expressions (#31)


### 18.3a1

* added `--check`

* only put trailing commas in function signatures and calls if it's
  safe to do so. If the file is Python 3.6+ it's always safe, otherwise
  only safe if there are no `*args` or `**kwargs` used in the signature
  or call. (#8)

* fixed invalid spacing of dots in relative imports (#6, #13)

* fixed invalid splitting after comma on unpacked variables in for-loops
  (#23)

* fixed spurious space in parenthesized set expressions (#7)

* fixed spurious space after opening parentheses and in default
  arguments (#14, #17)

* fixed spurious space after unary operators when the operand was
  a complex expression (#15)


### 18.3a0

* first published version, Happy 🍰 Day 2018!

* alpha quality

* date-versioned (see: https://calver.org/)
