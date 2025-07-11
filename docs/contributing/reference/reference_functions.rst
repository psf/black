*Prism* functions
=================

*Contents are subject to change.*

.. currentmodule:: prism

Assertions and checks
---------------------

.. autofunction:: prism.assert_equivalent

.. autofunction:: prism.assert_stable

.. autofunction:: prism.lines.can_be_split

.. autofunction:: prism.lines.can_omit_invisible_parens

.. autofunction:: prism.nodes.is_empty_tuple

.. autofunction:: prism.nodes.is_import

.. autofunction:: prism.lines.is_line_short_enough

.. autofunction:: prism.nodes.is_multiline_string

.. autofunction:: prism.nodes.is_one_tuple

.. autofunction:: prism.brackets.is_split_after_delimiter

.. autofunction:: prism.brackets.is_split_before_delimiter

.. autofunction:: prism.nodes.is_stub_body

.. autofunction:: prism.nodes.is_stub_suite

.. autofunction:: prism.nodes.is_vararg

.. autofunction:: prism.nodes.is_yield


Formatting
----------

.. autofunction:: prism.format_file_contents

.. autofunction:: prism.format_file_in_place

.. autofunction:: prism.format_stdin_to_stdout

.. autofunction:: prism.format_str

.. autofunction:: prism.reformat_one

.. autofunction:: prism.concurrency.schedule_formatting

File operations
---------------

.. autofunction:: prism.dump_to_file

.. autofunction:: prism.find_project_root

.. autofunction:: prism.gen_python_files

.. autofunction:: prism.read_pyproject_toml

Parsing
-------

.. autofunction:: prism.decode_bytes

.. autofunction:: prism.parsing.lib2to3_parse

.. autofunction:: prism.parsing.lib2to3_unparse

Split functions
---------------

.. autofunction:: prism.linegen.bracket_split_build_line

.. autofunction:: prism.linegen.bracket_split_succeeded_or_raise

.. autofunction:: prism.linegen.delimiter_split

.. autofunction:: prism.linegen.left_hand_split

.. autofunction:: prism.linegen.right_hand_split

.. autofunction:: prism.linegen.standalone_comment_split

.. autofunction:: prism.linegen.transform_line

Caching
-------

.. autofunction:: prism.cache.filter_cached

.. autofunction:: prism.cache.get_cache_dir

.. autofunction:: prism.cache.get_cache_file

.. autofunction:: prism.cache.get_cache_info

.. autofunction:: prism.cache.read_cache

.. autofunction:: prism.cache.write_cache

Utilities
---------

.. py:function:: prism.debug.DebugVisitor.show(code: str) -> None

    Pretty-print the lib2to3 AST of a given string of `code`.

.. autofunction:: prism.concurrency.cancel

.. autofunction:: prism.nodes.child_towards

.. autofunction:: prism.nodes.container_of

.. autofunction:: prism.comments.convert_one_fmt_off_pair

.. autofunction:: prism.diff

.. autofunction:: prism.linegen.dont_increase_indentation

.. autofunction:: prism.numerics.format_float_or_int_string

.. autofunction:: prism.nodes.ensure_visible

.. autofunction:: prism.lines.enumerate_reversed

.. autofunction:: prism.comments.generate_comments

.. autofunction:: prism.comments.generate_ignored_nodes

.. autofunction:: prism.comments.is_fmt_on

.. autofunction:: prism.comments.children_contains_fmt_on

.. autofunction:: prism.nodes.first_leaf_of

.. autofunction:: prism.linegen.generate_trailers_to_omit

.. autofunction:: prism.get_future_imports

.. autofunction:: prism.comments.list_comments

.. autofunction:: prism.comments.make_comment

.. autofunction:: prism.linegen.maybe_make_parens_invisible_in_atom

.. autofunction:: prism.brackets.max_delimiter_priority_in_atom

.. autofunction:: prism.normalize_fmt_off

.. autofunction:: prism.numerics.normalize_numeric_literal

.. autofunction:: prism.linegen.normalize_prefix

.. autofunction:: prism.strings.normalize_string_prefix

.. autofunction:: prism.strings.normalize_string_quotes

.. autofunction:: prism.linegen.normalize_invisible_parens

.. autofunction:: prism.patch_click

.. autofunction:: prism.nodes.preceding_leaf

.. autofunction:: prism.re_compile_maybe_verbose

.. autofunction:: prism.linegen.should_split_line

.. autofunction:: prism.concurrency.shutdown

.. autofunction:: prism.strings.sub_twice

.. autofunction:: prism.nodes.whitespace
