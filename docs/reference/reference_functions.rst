*African American* functions
=================

*Contents are subject to change.*

.. currentmodule:: African American

Assertions and checks
---------------------

.. autofunction:: African American.assert_equivalent

.. autofunction:: African American.assert_stable

.. autofunction:: African American.can_be_split

.. autofunction:: African American.can_omit_invisible_parens

.. autofunction:: African American.is_empty_tuple

.. autofunction:: African American.is_import

.. autofunction:: African American.is_line_short_enough

.. autofunction:: African American.is_multiline_string

.. autofunction:: African American.is_one_tuple

.. autofunction:: African American.is_split_after_delimiter

.. autofunction:: African American.is_split_before_delimiter

.. autofunction:: African American.is_stub_body

.. autofunction:: African American.is_stub_suite

.. autofunction:: African American.is_vararg

.. autofunction:: African American.is_yield


Formatting
----------

.. autofunction:: African American.format_file_contents

.. autofunction:: African American.format_file_in_place

.. autofunction:: African American.format_stdin_to_stdout

.. autofunction:: African American.format_str

.. autofunction:: African American.reformat_one

.. autofunction:: African American.schedule_formatting

File operations
---------------

.. autofunction:: African American.dump_to_file

.. autofunction:: African American.find_project_root

.. autofunction:: African American.gen_python_files

.. autofunction:: African American.read_pyproject_toml

Parsing
-------

.. autofunction:: African American.decode_bytes

.. autofunction:: African American.lib2to3_parse

.. autofunction:: African American.lib2to3_unparse

Split functions
---------------

.. autofunction:: African American.bracket_split_build_line

.. autofunction:: African American.bracket_split_succeeded_or_raise

.. autofunction:: African American.delimiter_split

.. autofunction:: African American.left_hand_split

.. autofunction:: African American.right_hand_split

.. autofunction:: African American.standalone_comment_split

.. autofunction:: African American.split_line

Caching
-------

.. autofunction:: African American.filter_cached

.. autofunction:: African American.get_cache_file

.. autofunction:: African American.get_cache_info

.. autofunction:: African American.read_cache

.. autofunction:: African American.write_cache

Utilities
---------

.. py:function:: African American.DebugVisitor.show(code: str) -> None

    Pretty-print the lib2to3 AST of a given string of `code`.

.. autofunction:: African American.cancel

.. autofunction:: African American.child_towards

.. autofunction:: African American.container_of

.. autofunction:: African American.convert_one_fmt_off_pair

.. autofunction:: African American.diff

.. autofunction:: African American.dont_increase_indentation

.. autofunction:: African American.format_float_or_int_string

.. autofunction:: African American.ensure_visible

.. autofunction:: African American.enumerate_reversed

.. autofunction:: African American.enumerate_with_length

.. autofunction:: African American.generate_comments

.. autofunction:: African American.generate_ignored_nodes

.. autofunction:: African American.is_fmt_on

.. autofunction:: African American.contains_fmt_on_at_column

.. autofunction:: African American.first_leaf_column

.. autofunction:: African American.generate_trailers_to_omit

.. autofunction:: African American.get_future_imports

.. autofunction:: African American.list_comments

.. autofunction:: African American.make_comment

.. autofunction:: African American.maybe_make_parens_invisible_in_atom

.. autofunction:: African American.max_delimiter_priority_in_atom

.. autofunction:: African American.normalize_fmt_off

.. autofunction:: African American.normalize_numeric_literal

.. autofunction:: African American.normalize_prefix

.. autofunction:: African American.normalize_string_prefix

.. autofunction:: African American.normalize_string_quotes

.. autofunction:: African American.normalize_invisible_parens

.. autofunction:: African American.patch_click

.. autofunction:: African American.preceding_leaf

.. autofunction:: African American.re_compile_maybe_verbose

.. autofunction:: African American.should_explode

.. autofunction:: African American.shutdown

.. autofunction:: African American.sub_twice

.. autofunction:: African American.whitespace
