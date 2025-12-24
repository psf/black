# Doctest Formatting

While *Black* makes some decisions about styling for docstrings, it does not make any assumptions about the contents of documentation. Thus, executable Python code inside docstrings or documentation files (e.g. doctests), will not be formatted by *Black*.

Listed below are tools that apply *Black* formatting to code inside docstrings and documentation files.

## blackdoc

[`blackdoc`](https://pypi.org/project/blackdoc/) is primarily used to apply *Black* formatting to doctests in Python files. It will not format any file contents that are otherwise covered by *Black*.

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

- Python code blocks in Markdown or reStructuredText files. In these cases, normal *Black* formatting is applied, i.e., doctests inside Python code blocks will not be formatted.

    ````markdown
    ```python
    print("Hello world!")
    ```
    ````

    ```rst
    .. code-block:: python
        print("Hello world!")
    ```

## blacken-docs

[`blacken-docs`](https://pypi.org/project/blacken-docs/) is primarly used to apply *Black* formatting to code in documentation files (e.g. `.rst`, `.md`, `.tex`).

`blacken-docs` supports the following:

- Python code blocks in Markdown, reStructuredText, and LaTeX files. Similar to `blackdoc`, normal *Black* formatting is applied, so doctests inside Python code blocks will not be formatted.

    ````markdown
    ```python
    print("Hello world!")
    ```
    ````

    ```rst
    .. code-block:: python
        print("Hello world!")
    ```

    ```latex
    \begin{minted}{python}
    print("Hello world!")
    \end{minted}
    ```

- Doctests inside Pycon code blocks in Markdown and reStructuredText. The code blocks may be included in a `.md` or `.rst` file, or inside a docstring in a Python file.

    ````markdown
    ```pycon
    >>> print("Hello world!")
    ```
    ````

    ```rst
    .. code-block:: pycon
        >>> print("Hello world!")
    ```

    ```python
    def add_one(n: int) -> int:
        """
        Examples
        --------
        ```pycon
        >>> add_one(1) == 2
        ```
        """
        return n + 1
    ```

</br>

> Note: There are some observed inconsistencies between the above packages. Because of this, we hesitate to make any recommendations. We also encourage anyone to contribute documentation for additional packages that apply *Black* formatting to doctests.