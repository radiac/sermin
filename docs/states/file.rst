=================
The File state
=================

.. autoclass:: sermin.File
    :members:


File Parsers
============

File parsers are used for applying ``set`` and ``delete`` arguments of the
``File`` state.


Built-in parsers
----------------

.. autoclass:: sermin.AppendParser
    :members:


.. autoclass:: sermin.IniParser
    :members:


Writing a custom parser
-----------------------

Subclass the ``FileParser`` base class, and pass it into the ``File`` state
definition on the ``parser`` argument.

.. autoclass:: sermin.FileParser
    :members:

