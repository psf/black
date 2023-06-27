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

:class:`DebugVisitor`
------------------------

.. autoclass:: black.debug.DebugVisitor
    :show-inheritance:
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

:class:`MagicFinder`
------------------------

.. autoclass:: black.handle_ipynb_magics.MagicFinder
    :show-inheritance:
    :members:

Enum Classes
~~~~~~~~~~~~~

Classes inherited from Python `Enum <https://docs.python.org/3/library/enum.html#enum.Enum>`_ class.

:class:`Changed`
----------------

.. autoclass:: black.Changed
    :show-inheritance:
    :members:


:class:`WriteBack`
------------------

.. autoclass:: black.WriteBack
    :show-inheritance:
    :members:

:class:`TargetVersion`
----------------------

.. autoclass:: black.TargetVersion
    :show-inheritance:
    :members:

:class:`Feature`
------------------

.. autoclass:: black.Feature
    :show-inheritance:
    :members:

:class:`Preview`
------------------

.. autoclass:: black.mode.Preview
    :show-inheritance:
    :members:
