## Change Log

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
