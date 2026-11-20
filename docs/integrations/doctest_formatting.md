# Doctest Formatting

While _Black_ makes some decisions about styling for docstrings, it does not make any
assumptions about the contents of documentation. Thus, executable Python code inside
docstrings or documentation files (e.g. doctests), will not be formatted by _Black_.

Listed below are tools that apply _Black_ formatting to code inside docstrings and
documentation files.

> Note: There are some observed inconsistencies between the below packages. Because of
> this, we hesitate to make any recommendations. Any installed packages are installed at
> your own risk. We also encourage anyone to contribute documentation for additional
> packages that apply _Black_ formatting to doctests.

## blacken-docs

[`blacken-docs`](https://github.com/adamchainz/blacken-docs) is primarily used to apply
_Black_ formatting to code in documentation files (e.g. `.rst`, `.md`, `.tex`).

`blacken-docs` supports Python code blocks and Pycon doctests in Markdown,
reStructuredText, and LaTeX files, as well as Python docstrings containing Markdown code
blocks and Pycon doctests. It will not format any file contents that _Black_ will
already format.

````md
```python
print("Hello world!")
```

```pycon
>>> print("Hello world!")
```
````

```rst
.. code-block:: python
    print("Hello world!")

.. code-block:: pycon
    >>> print("Hello world!")
```

```latex
\begin{pycode}
print("hello world")
\end{pycode}

\begin{minted}{pycon}
>>> print("hello world")
\end{minted}
```

````python
"""
```python
print("Hello world!")
```
"""

def add_one(n: int) -> int:
    """
    Examples
    --------
    ```pycon
    >>> add_one(1) == 2
    ```
    """
    return n + 1
````

## blackdoc

[`blackdoc`](https://blackdoc.readthedocs.io/en/stable) is primarily used to apply
_Black_ formatting to doctests in Python files. It will not format any file contents
that _Black_ will already format.

`blackdoc` supports the following:

- Doctests in Python files.

  ```python
  def add_one(n: int) -> int:
      """
      Examples
      --------
      >>> add_one(1) == 2
      """
      return n + 1
  ```

- Python code blocks and doctests in reStructuredText files.

  ```rst
  .. code-block:: python
     print("Hello world!")

  >>> print("Hello world!")
  ```
