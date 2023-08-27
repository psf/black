*Black* classes
===============

*Contents are subject to change.*

Black Classes
~~~~~~~~~~~~~~

.. currentmodule:: black

:class:`BracketTracker`
-----------------------

.. autoclass:: black.brackets.BracketTracker
    :members:

:class:`Line`
-------------

.. autoclass:: black.lines.Line
    :members:
    :special-members: __str__, __bool__

:class:`RHSResult`
-------------------------

.. autoclass:: black.lines.RHSResult
    :members:

:class:`LinesBlock`
-------------------------

.. autoclass:: black.lines.LinesBlock
    :members:

:class:`EmptyLineTracker`
-------------------------

.. autoclass:: black.lines.EmptyLineTracker
    :members:

:class:`LineGenerator`
----------------------

.. autoclass:: black.linegen.LineGenerator
    :show-inheritance:
    :members:

:class:`ProtoComment`
---------------------

.. autoclass:: black.comments.ProtoComment
    :members:

:class:`Mode`
---------------------

.. autoclass:: black.mode.Mode
    :members:

:class:`Report`
---------------

.. autoclass:: black.report.Report
    :members:
    :special-members: __str__

:class:`Ok`
---------------

.. autoclass:: black.rusty.Ok
    :show-inheritance:
    :members:

:class:`Err`
---------------

.. autoclass:: black.rusty.Err
    :show-inheritance:
    :members:

:class:`Visitor`
----------------

.. autoclass:: black.nodes.Visitor
    :show-inheritance:
    :members:

:class:`StringTransformer`
----------------------------

.. autoclass:: black.trans.StringTransformer
    :show-inheritance:
    :members:

:class:`CustomSplit`
----------------------------

.. autoclass:: black.trans.CustomSplit
    :members:

:class:`CustomSplitMapMixin`
-----------------------------

.. autoclass:: black.trans.CustomSplitMapMixin
    :show-inheritance:
    :members:

:class:`StringMerger`
----------------------

.. autoclass:: black.trans.StringMerger
    :show-inheritance:
    :members:

:class:`StringParenStripper`
-----------------------------

.. autoclass:: black.trans.StringParenStripper
    :show-inheritance:
    :members:

:class:`BaseStringSplitter`
-----------------------------

.. autoclass:: black.trans.BaseStringSplitter
    :show-inheritance:
    :members:

:class:`StringSplitter`
-----------------------------

.. autoclass:: black.trans.StringSplitter
    :show-inheritance:
    :members:

:class:`StringParenWrapper`
-----------------------------

.. autoclass:: black.trans.StringParenWrapper
    :show-inheritance:
    :members:

:class:`StringParser`
-----------------------------

.. autoclass:: black.trans.StringParser
    :members:

:class:`DebugVisitor`
------------------------

.. autoclass:: black.debug.DebugVisitor
    :show-inheritance:
    :members:

:class:`Replacement`
------------------------

.. autoclass:: black.handle_ipynb_magics.Replacement
    :members:

:class:`CellMagic`
------------------------

.. autoclass:: black.handle_ipynb_magics.CellMagic
    :members:

:class:`CellMagicFinder`
------------------------

.. autoclass:: black.handle_ipynb_magics.CellMagicFinder
    :show-inheritance:
    :members:

:class:`OffsetAndMagic`
------------------------

.. autoclass:: black.handle_ipynb_magics.OffsetAndMagic
    :members:

:class:`MagicFinder`
------------------------

.. autoclass:: black.handle_ipynb_magics.MagicFinder
    :show-inheritance:
    :members:

:class:`Cache`
------------------------

.. autoclass:: black.cache.Cache
    :show-inheritance:
    :members:

Enum Classes
~~~~~~~~~~~~~

Classes inherited from Python `Enum <https://docs.python.org/3/library/enum.html#enum.Enum>`_ class.

:class:`Changed`
----------------

.. autoclass:: black.report.Changed
    :show-inheritance:
    :members:

:class:`WriteBack`
------------------

.. autoclass:: black.WriteBack
    :show-inheritance:
    :members:

:class:`TargetVersion`
----------------------

.. autoclass:: black.mode.TargetVersion
    :show-inheritance:
    :members:

:class:`Feature`
------------------

.. autoclass:: black.mode.Feature
    :show-inheritance:
    :members:

:class:`Preview`
------------------

.. autoclass:: black.mode.Preview
    :show-inheritance:
    :members:
