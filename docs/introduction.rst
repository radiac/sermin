============
Introduction
============

Features
========

* Define states in python scripts and modules
* States applied in code order
* Everything written in python
* Features: dry run


Quickstart
==========

Sermin takes a system state defined in a `blueprint <blueprints>`_ (a python
script which defines `states <states_api>`_ as Python classes and functions),
and applies them to the system.


Install::

    pip install sermin

Create a blueprint and save it as `blueprint.py`::

    from sermin import Package, File

    Package('nginx')
    File('/var/www/html/index.html', source='index.html')

See what changes it will make::

    sermin blueprint.py --dry

Apply the changes::

    sermin blueprint.py


FAQ
===

How does it compare to Puppet or Ansible?
-----------------------------------------

* Sermin states are written directly in Python, so there are none of the same
  complications you get when trying to use programming constructs in YAML or
  Puppet's DSL, and no need to define your states in multiple languages.
* No dependency graph magic or conflicts - states are applied in code order.
* No master/slave or automated pull deployment - blueprints can either be run
  locally, or run over SSH from any machine with the appropriate credentials.
