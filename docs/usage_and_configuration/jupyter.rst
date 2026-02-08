=======
Jupyter
=======

Installation
============

If you want to format Jupyter Notebooks, install with:

.. code-block:: bash

    pip install "black[jupyter]"

Usage
=====

Black can format Jupyter Notebooks alongside your regular Python files. Once installed with the ``jupyter`` extra, Black will automatically recognize and format ``.ipynb`` files.

Basic usage:

.. code-block:: bash

    black notebook.ipynb

Or format entire directories containing both Python files and notebooks:

.. code-block:: bash

    black src/

Command-Line Options
====================

``--ipynb``
-----------

Format all input files like Jupyter Notebooks regardless of file extension. This is useful when piping source on standard input.

``--python-cell-magics``
-------------------------

When processing Jupyter Notebooks, add the given magic to the list of known python-magics. Useful for formatting cells with custom python magics.

Frequently Asked Questions
===========================

Why is my Jupyter Notebook cell not formatted?
-----------------------------------------------

Black is timid about formatting Jupyter Notebooks. Cells containing any of the following will not be formatted:

- automagics (e.g. ``pip install black``)
- non-Python cell magics (e.g. ``%%writefile``). These can be added with the flag ``--python-cell-magics``, e.g. ``black --python-cell-magics writefile hello.ipynb``.
- multiline magics, e.g.:

  .. code-block:: python

      %timeit f(1, \
              2, \
              3)

- code which IPython's ``TransformerManager`` would transform magics into, e.g.:

  .. code-block:: python

      get_ipython().system('ls')

- invalid syntax, as it can't be safely distinguished from automagics in the absence of a running IPython kernel.
