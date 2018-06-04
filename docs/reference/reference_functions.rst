*Black* functions
=================

*Contents are subject to change.*

.. currentmodule:: black

Assertions and checks
---------------------

.. autofunction:: black.assert_equivalent

.. autofunction:: black.assert_stable

.. autofunction:: black.can_omit_invisible_parens

.. autofunction:: black.is_empty_tuple

.. autofunction:: black.is_import

.. autofunction:: black.is_line_short_enough

.. autofunction:: black.is_multiline_string

.. autofunction:: black.is_one_tuple

.. autofunction:: black.is_python36

.. autofunction:: black.is_split_after_delimiter

.. autofunction:: black.is_split_before_delimiter

.. autofunction:: black.is_stub_body

.. autofunction:: black.is_stub_suite

.. autofunction:: black.is_vararg

.. autofunction:: black.is_yield


Formatting
----------

.. autofunction:: black.format_file_contents

.. autofunction:: black.format_file_in_place

.. autofunction:: black.format_stdin_to_stdout

.. autofunction:: black.format_str

.. autofunction:: black.reformat_one

.. autofunction:: black.schedule_formatting

File operations
---------------

.. autofunction:: black.dump_to_file

.. autofunction:: black.gen_python_files_in_dir

Parsing
-------

.. autofunction:: black.decode_bytes

.. autofunction:: black.lib2to3_parse

.. autofunction:: black.lib2to3_unparse

Split functions
---------------

.. autofunction:: black.delimiter_split

.. autofunction:: black.left_hand_split

.. autofunction:: black.right_hand_split

.. autofunction:: black.standalone_comment_split

.. autofunction:: black.split_line

.. autofunction:: black.bracket_split_succeeded_or_raise

Caching
-------

.. autofunction:: black.filter_cached

.. autofunction:: black.get_cache_info

.. autofunction:: black.read_cache

.. autofunction:: black.write_cache

Utilities
---------

.. py:function:: black.DebugVisitor.show(code: str) -> None

    Pretty-print the lib2to3 AST of a given string of `code`.

.. autofunction:: black.diff

.. autofunction:: black.ensure_visible

.. autofunction:: black.enumerate_reversed

.. autofunction:: black.enumerate_with_length

.. autofunction:: black.generate_comments

.. autofunction:: black.make_comment

.. autofunction:: black.maybe_make_parens_invisible_in_atom

.. autofunction:: black.max_delimiter_priority_in_atom

.. autofunction:: black.normalize_prefix

.. autofunction:: black.normalize_string_quotes

.. autofunction:: black.normalize_invisible_parens

.. autofunction:: black.preceding_leaf

.. autofunction:: black.sub_twice

.. autofunction:: black.whitespace
