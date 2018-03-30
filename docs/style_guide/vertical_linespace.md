# Vertical whitespace

*Black* tries to render one full expression or simple statement per line.

## Rendering on one line fits alloted line-length

### Original

```py3
l = [1,
    2,
    3,
]
```
### After *Black*

```py3
l = [1, 2, 3]
```

## Rendering on one line exceeds alloted line-length

If the render exceeds the allotted line length, *Black* looks next at 
the contents of the first outer matching brackets and places that in its own
indented line.

### Original

```py3
l = [[n for n in list_bosses()], [n for n in list_employees()]]
```
### After *Black*

```py3
l = [
    [n for n in list_bosses()], [n for n in list_employees()]
]
```

## Apply previous rule recursively when needed

### Original

```py3
def very_important_function(template: str, *variables, file: os.PathLike, debug: bool = False):
    """Applies `variables` to the `template` and writes to `file`."""
    with open(file, 'w') as f:
        ...
```

### After *Black*

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

If the contents of the matching brackets pair
are comma-separated (like an argument list, or a dict literal, and so on)
then *Black* will first try to keep them on the same line with the
matching brackets.  If that doesn't work, it will put all of them in
separate lines.

*Notice*: Closing brackets are always dedented, and a trailing comma is always
added.