=============
Ad-hoc states
=============

Sometimes you'll want to perform an action without wanting the overhead of
defining a `custom state <custom>`_.

You can use the decorators ``check`` and ``apply`` to define functions which
will be treated as instantiated states - ie they will be run when Sermin
reaches their definition.

.. autofunction:: sermin.check

.. autofunction:: sermin.apply
