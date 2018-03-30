## Line wrap and whitespace

*Black* ignores previous formatting and applies uniform horizontal
and vertical whitespace to your code. *Black*'s coding style can be viewed as
a strict subset of PEP 8.

### Horizontal whitespace

The rule for horizontal is: "Do whatever makes `pycodestyle` happy."

### Vertical whitespace

*Black* tries to render one full expression or simple statement per line.

If the render fits the alloted line length, *Black* uses it:

*Input*
```py3
l = [1,
    2,
    3,
]
```

**Black**
```py3
l = [1, 2, 3]
```

If the render exceeds the allotted line length, *Black* looks next at 
the contents of the first outer matching brackets and put that in a separate
indented line:

*Input*
```py3
l = [[n for n in list_bosses()], [n for n in list_employees()]]
```

**Black**
```py3
l = [
    [n for n in list_bosses()], [n for n in list_employees()]
]
```

If this would still exceed the allotted line length, *Black* will
recursively decompose the internal expression further using the same rule, 
indenting matching brackets every time. 

If the contents of the matching brackets pair
are comma-separated (like an argument list, or a dict literal, and so on)
then *Black* will first try to keep them on the same line with the
matching brackets.  If that doesn't work, it will put all of them in
separate lines.

*Input*
```py3
def very_important_function(template: str, *variables, file: os.PathLike, debug: bool = False):
    """Applies `variables` to the `template` and writes to `file`."""
    with open(file, 'w') as f:
        ...
```

**Black**
```py3
def very_important_function(
    template: str,
    *variables,
    file: os.PathLike,
    debug: bool = False,
):
    """Applies `variables` to the `template` and writes to `file`."""
    with open(file, 'w') as f:
        ...
```

*Notice*: Closing brackets are always dedented, and a trailing comma is always
added. **Black philosophy**:

- This produces smaller diffs.
- When you add or remove an element, it's always just one line.
- Having the closing bracket dedented provides a clear delimiter
  between two distinct sections of the code that otherwise share the same
  indentation level (like the arguments list and the docstring in the
  example above).
