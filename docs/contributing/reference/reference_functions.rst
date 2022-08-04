*Black* functions
=================

*Contents are subject to change.*

.. currentmodule:: black

Assertions and checks
---------------------

.. autofunction:: black.assert_equivalent

.. autofunction:: black.assert_stable

.. autofunction:: black.lines.can_be_split

.. autofunction:: black.lines.can_omit_invisible_parens

.. autofunction:: black.nodes.is_empty_tuple

.. autofunction:: black.nodes.is_import

.. autofunction:: black.lines.is_line_short_enough

.. autofunction:: black.nodes.is_multiline_string

.. autofunction:: black.nodes.is_one_tuple

.. autofunction:: black.brackets.is_split_after_delimiter

.. autofunction:: black.brackets.is_split_before_delimiter

.. autofunction:: black.nodes.is_stub_body

.. autofunction:: black.nodes.is_stub_suite

.. autofunction:: black.nodes.is_vararg

.. autofunction:: black.nodes.is_yield


Formatting
----------

.. autofunction:: black.format_file_contents

.. autofunction:: black.format_file_in_place

.. autofunction:: black.format_stdin_to_stdout

.. autofunction:: black.format_str

.. autofunction:: black.reformat_one

.. autofunction:: black.concurrency.schedule_formatting

File operations
---------------

.. autofunction:: black.dump_to_file

.. autofunction:: black.find_project_root

.. autofunction:: black.gen_python_files

.. autofunction:: black.read_pyproject_toml

Parsing
-------

.. autofunction:: black.decode_bytes

.. autofunction:: black.parsing.lib2to3_parse

.. autofunction:: black.parsing.lib2to3_unparse

Split functions
---------------

.. autofunction:: black.linegen.bracket_split_build_line

.. autofunction:: black.linegen.bracket_split_succeeded_or_raise

.. autofunction:: black.linegen.delimiter_split

.. autofunction:: black.linegen.left_hand_split

.. autofunction:: black.linegen.right_hand_split

.. autofunction:: black.linegen.standalone_comment_split

.. autofunction:: black.linegen.transform_line

Caching
-------

.. autofunction:: black.cache.filter_cached

.. autofunction:: black.cache.get_cache_dir

.. autofunction:: black.cache.get_cache_file

.. autofunction:: black.cache.get_cache_info

.. autofunction:: black.cache.read_cache

.. autofunction:: black.cache.write_cache

Utilities
---------

.. py:function:: black.debug.DebugVisitor.show(code: str) -> None

    Pretty-print the lib2to3 AST of a given string of `code`.

.. autofunction:: black.concurrency.cancel

.. autofunction:: black.nodes.child_towards

.. autofunction:: black.nodes.container_of

.. autofunction:: black.comments.convert_one_fmt_off_pair

.. autofunction:: black.diff

.. autofunction:: black.linegen.dont_increase_indentation

.. autofunction:: black.numerics.format_float_or_int_string

.. autofunction:: black.nodes.ensure_visible

.. autofunction:: black.lines.enumerate_reversed

.. autofunction:: black.comments.generate_comments

.. autofunction:: black.comments.generate_ignored_nodes

.. autofunction:: black.comments.is_fmt_on

.. autofunction:: black.comments.contains_fmt_on_at_column

.. autofunction:: black.nodes.first_leaf_column

.. autofunction:: black.linegen.generate_trailers_to_omit

.. autofunction:: black.get_future_imports

.. autofunction:: black.comments.list_comments

.. autofunction:: black.comments.make_comment

.. autofunction:: black.linegen.maybe_make_parens_invisible_in_atom

.. autofunction:: black.brackets.max_delimiter_priority_in_atom

.. autofunction:: black.normalize_fmt_off

.. autofunction:: black.numerics.normalize_numeric_literal

.. autofunction:: black.linegen.normalize_prefix

.. autofunction:: black.strings.normalize_string_prefix

.. autofunction:: black.strings.normalize_string_quotes

.. autofunction:: black.linegen.normalize_invisible_parens

.. autofunction:: black.patch_click

.. autofunction:: black.nodes.preceding_leaf

.. autofunction:: black.re_compile_maybe_verbose

.. autofunction:: black.linegen.should_split_line

.. autofunction:: black.concurrency.shutdown

.. autofunction:: black.strings.sub_twice

.. autofunction:: black.nodes.whitespace
