The Black Code Style
====================

.. toctree::
    :hidden:

    Current style <current_style>
    Future style <future_style>

*Black* is a PEP 8 compliant opinionated formatter with its own style.

While keeping the style unchanged throughout releases has always been a
goal, the *Black* code style has never been set in stone. Sometimes it's modified in response to
user feedback or even changes to the Python language!

Starting from January 2022, we will follow a more formal stability policy:

- *Black* guarantees that the same code, formatted with the same options,
  will produce the same output for all releases in a given calendar year.
  This means projects can safely use black ~= 22.0 without worrying about
  major formatting changes disrupting their project in 2022. We may still
  fix bugs where *Black* crashes on some code, and make other improvements
  that do not affect formatting.
- We will have an ``--future`` flag that may produce different
  formatting output. We make no guarantee about the stability of this flag
  between releases. At the end of the year, we will evaluate anything we
  put under the ``--future`` flag and if we are happy with it, the
  style change will be promoted to the stable style for the next year.

At the same time, we will finally drop the beta marker from our releases,
and we will drop support for Python 2.
The first release to follow the new policy will be 22.0.0.

Documentation for both the current and future styles can be found:

- :doc:`current_style`
- :doc:`future_style`
