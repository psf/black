.. black documentation master file, created by
   sphinx-quickstart on Fri Mar 23 10:53:30 2018.

The uncompromising code formatter
=================================

By using *Black*, you agree to cede control over minutiae of
hand-formatting. In return, *Black* gives you speed, determinism, and
freedom from `pycodestyle` nagging about formatting. You will save time
and mental energy for more important matters.

*Black* makes code review faster by producing the smallest diffs
possible. Blackened code looks the same regardless of the project
you're reading. Formatting becomes transparent after a while and you
can focus on the content instead.

Try it out now using the `Black Playground <https://black.vercel.app>`_.

.. admonition:: Note - this is a beta product

   *Black* is already `successfully used <https://github.com/psf/black#used-by>`_ by
   many projects, small and big. *Black* has a comprehensive test suite, with efficient
   parallel tests, our own auto  formatting and parallel Continuous Integration runner.
   However, *Black* is still beta. Things will probably be wonky for a while. This is
   made explicit by the "Beta" trove classifier, as well as by the "b" in the version
   number. What this means for you is that **until the formatter becomes stable, you
   should expect some formatting to change in the future**. That being said, no drastic
   stylistic changes are planned, mostly responses to bug reports.

   Also, as a safety measure which slows down processing, *Black* will check that the
   reformatted code still produces a valid AST that is effectively equivalent to the
   original (see the
   `Pragmatism <./the_black_code_style/current_style.html#pragmatism>`_
   section for details). If you're feeling confident, use ``--fast``.

.. note::
   :doc:`Black is licensed under the MIT license <license>`.

Testimonials
------------

**Mike Bayer**, author of `SQLAlchemy <https://www.sqlalchemy.org/>`_:

   *I can't think of any single tool in my entire programming career that has given me a
   bigger productivity increase by its introduction. I can now do refactorings in about
   1% of the keystrokes that it would have taken me previously when we had no way for
   code to format itself.*

**Dusty Phillips**, `writer <https://smile.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=dusty+phillips>`_:

   *Black is opinionated so you don't have to be.*

**Hynek Schlawack**, creator of `attrs <https://www.attrs.org/>`_, core
developer of Twisted and CPython:

   *An auto-formatter that doesn't suck is all I want for Xmas!*

**Carl Meyer**, `Django <https://www.djangoproject.com/>`_ core developer:

   *At least the name is good.*

**Kenneth Reitz**, creator of `requests <http://python-requests.org/>`_
and `pipenv <https://docs.pipenv.org/>`_:

   *This vastly improves the formatting of our code. Thanks a ton!*


Show your style
---------------

Use the badge in your project's README.md:

.. code-block:: md

   [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


Using the badge in README.rst:

.. code-block:: rst

   .. image:: https://img.shields.io/badge/code%20style-black-000000.svg
      :target: https://github.com/psf/black

Looks like this:

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black

Contents
--------

.. toctree::
   :maxdepth: 3
   :includehidden:

   the_black_code_style/index

.. toctree::
   :maxdepth: 3
   :includehidden:

   getting_started
   usage_and_configuration/index
   integrations/index
   guides/index
   faq

.. toctree::
   :maxdepth: 3
   :includehidden:

   contributing/index
   change_log
   authors

.. toctree::
   :hidden:

   GitHub ↪ <https://github.com/psf/black>
   PyPI ↪ <https://pypi.org/project/black>
   IRC ↪ <https://webchat.freenode.net/?channels=%23blackformatter>

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
