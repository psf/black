The Black Code Style
====================

.. toctree::
    :hidden:

    Current style <current_style>
    Future style <future_style>

*Black* is a PEP 8 compliant opinionated formatter with its own style.

While keeping the style unchanged throughout releases has always been a goal,
the *Black* code style isn't set in stone. It evolves to accommodate for new features
in the Python language and, occasionally, in response to user feedback.
Large-scale style preferences presented in :doc:`current_style` are very unlikely to
change, but minor style aspects and details might change according to the stability
policy presented below. Ongoing style considerations are tracked on GitHub with the
`design <https://github.com/psf/black/labels/T%3A%20design>`_ issue label.

Stability Policy
----------------

The following policy applies for the *Black* code style, in non pre-release
versions of *Black*:

- The same code, formatted with the same options, will produce the same
  output for all releases in a given calendar year.

  This means projects can safely use `black ~= 22.0` without worrying about
  major formatting changes disrupting their project in 2022. We may still
  fix bugs where *Black* crashes on some code, and make other improvements
  that do not affect formatting.

- The first release in a new calendar year *may* contain formatting changes,
  although these will be minimised as much as possible. This is to allow for
  improved formatting enabled by newer Python language syntax as well as due
  to improvements in the formatting logic.

- The ``--preview`` flag is exempt from this policy. There are no guarantees
  around the stability of the output with that flag passed into *Black*. This
  flag is intended for allowing experimentation with the proposed changes to
  the *Black* code style.

Documentation for both the current and future styles can be found:

- :doc:`current_style`
- :doc:`future_style`
