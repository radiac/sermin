=======================
Defining a custom State
=======================

You can define States for use in your blueprints by subclassing the ``State``
base class.

.. autoclass:: sermin.State
    :members:


State settings
==============

Define settings for your state as ``Setting``  are namepace

.. py:attribute:: __namespace__

Specify the namespace for settings in this file by setting this variable to
a string.

If you do not specify a namespace, Sermin will check any ancestor modules for a
namespace definition, eg if the file is ``mymodule/foo/bar.py`` it will look
for a ``__namespace__`` instance defined in ``mymodule`` and ``mymodule.foo``.

If you do not specify a namespace and one is not found in an ancestor module,
one will be created based on the name of the file, eg ``myscript.py`` will
have the namespace `myscript`, or ``foo/__init__.py`` would have the namespace
``foo``. The file ``foo/bar.py`` would inherit the ``foo`` namespace.

Namespaces are case insensitive and can only contain the characters a-z and
``_`` underscore - dashes are not allowed. They must be unique.

Example::

    __namespace__ = 'mymodule'

.. autoclass:: sermin.Setting
    :members:


Example::

    arg = Setting('my-boolean-arg', bool)
    other = Setting('my-boolean-arg', bool, namespace='alternative_namespace')
    print(arg.value)

Command line is parsed, then arguments are parsed as they are defined so that
they are immediately available in the rest of your code. Invalid command line
arguments are only detected at the end of import.


Child states
============

If a State instance is defined as an attribute of another State, it will be
checked or applied once, regardless of the number of child states.

Child state instances will be removed from the registry root order.
