*Black* functions
=================

*Contents are subject to change.*

.. currentmodule:: black

Assertions and checks
---------------------

.. autofunction:: black.assert_equivalent

.. autofunction:: black.assert_stable

.. autofunction:: black.is_delimiter

.. autofunction:: black.is_import

.. autofunction:: black.is_python36

Formatting
----------

.. autofunction:: black.format_file_contents

.. autofunction:: black.format_file_in_place

.. autofunction:: black.format_stdin_to_stdout

.. autofunction:: black.format_str

.. autofunction:: black.schedule_formatting

File operations
---------------

.. autofunction:: black.dump_to_file

.. autofunction:: black.gen_python_files_in_dir

Parsing
-------

.. autofunction:: black.lib2to3_parse

.. autofunction:: black.lib2to3_unparse

Split functions
---------------

.. autofunction:: black.delimiter_split

.. autofunction:: black.left_hand_split

.. autofunction:: black.right_hand_split

.. autofunction:: black.split_line

.. autofunction:: black.split_succeeded_or_raise

Utilities
---------

.. autofunction:: black.diff

.. autofunction:: black.generate_comments

.. autofunction:: black.make_comment

.. autofunction:: black.normalize_prefix

.. autofunction:: black.preceding_leaf

.. autofunction:: black.whitespace