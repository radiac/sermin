======
Sermin
======

Python framework for defining and applying system states.


Quickstart
==========

Install::

    pip install sermin

Create `blueprint.py`::

    from sermin import Package, File

    Package('nginx', state=Package.INSTALLED)
    File('/var/www/html/index.html', source='index.html', state=EXISTS)

Run::

    sermin blueprint.py

This example will ensure nginx is installed, and ensure there is a file in
``/var/www/html`` called ``index.html``, which is a copy of the ``index.html``
next to your blueprint.
