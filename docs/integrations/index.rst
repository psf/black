Integrations
============

.. toctree::
    :hidden:

    editors
    github_actions
    source_version_control

*Black* can be integrated into many environments, providing a better and smoother experience. Documentation for integrating *Black* with a tool can be found for the
following areas:

- :doc:`Editor / IDE <./editors>`
- :doc:`GitHub Actions <./github_actions>`
- :doc:`Source version control <./source_version_control>`

Editors and tools not listed will require external contributions.

Patches welcome! ✨ 🍰 ✨

Any tool can pipe code through *Black* using its stdio mode (just
`use \`-\` as the file name <https://www.tldp.org/LDP/abs/html/special-chars.html#DASHREF2>`_).
The formatted code will be returned on stdout (unless ``--check`` was passed). *Black*
will still emit messages on stderr but that shouldn't affect your use case.

This can be used for example with PyCharm's or IntelliJ's
`File Watchers <https://www.jetbrains.com/help/pycharm/file-watchers.html>`_.
