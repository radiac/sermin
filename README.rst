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

    Package('nginx')
    File('/var/www/html/index.html', source='index.html')

Run::

    sermin blueprint.py
