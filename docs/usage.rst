=====
Usage
=====

The ``sermin`` command
======================

Usage::

    sermin [<blueprint>] [<named args>]

See :ref:`specifying_a_blueprint` and :ref:`specifying_arguments` for more
details.


If for some reason you don't want to or can't use the sermin command, you can
also run the package from the command line::

    python -m sermin [<blueprint>] [<named args>]


Examples
--------

Apply the script ``myscript.py``::

    sermin path/to/myscript.py

Push the ``state`` directory to the hosts and apply the ``mymodule`` module (ie
``state/mymodule.py`` or ``state/mymodule/__init__.py``)::

    sermin mymodule --source=path/to/state --host=foo.example.com

Pull the latest version of the git repository and apply the script
``script.py`` from inside it::

    sermin script.py --source=git+ssh://git.example.com/state.git

Download the state to the host, check the module ``host_foo`` inside it against
the host's state, but do not make any changes::

    sermin host_foo --source=https://example.com/state.tgz --host=foo.example.com --dry


.. _specifying_a_blueprint:

Specifying a blueprint
----------------------

The ``sermin`` command takes one unnamed argument, which is the blueprint
script's filename, or the blueprint module.

By default Sermin expects the blueprint to be in the current directory, but
this can be changed with the ``--source`` argument.

A ``--source`` can be one of:

* **Path to directory**
    Path to a local directory containing the blueprint - adds it to the
    python path.

    Because this allows you to break up your state definition into packages
    and modules within the directory, it is useful when you want to manage
    complex states, or multiple hosts with a mix of roles.

    If a ``--host`` is provided, the directory will be sent to the host.
    However, the whole directory will be sent each time, so it is less
    efficient than using git.

    Examples:

    * ``sermin mymodule --source=path/to/state``
    * ``sermin --source=path/to/state subdir/script.py``

* **HTTP URL**
    An HTTP (or HTTPS) URL to a zipped directory. Recognised extensions are
    ``zip``, ``tgz`` or ``tar.gz``.

    Examples:

    * ``sermin myscript.py --source=https://example.com/state.tgz``

* **Git URL**
    A URL to a git repository. This starts ``git+``, followed by whatever
    argument to be passed to ``git clone`` (see the git documentation for
    `Git URLs <https://git-scm.com/docs/git-clone>`_ for what it supports).

    If the repository has already been cloned, it will be updated with
    ``git pull`` - or to be precise::

        git fetch origin master
        git reset --hard FETCH_HEAD
        git clean -df

    Examples:

    * ``sermin --source=git+ssh://git.example.com/state.git roles/web.py``
    * ``sermin web --source=git+https://github.com/example/states.git``


.. _specifying_arguments:

Specifying arguments
--------------------

Sermin expects one unnamed argument, the blueprint for the state definitions -
see :ref:`specifying_a_blueprint` for details.

Arguments for modules are namespaced to avoid collisions, using the format
``--[namespace]:[arg]``.

It can then take multiple named arguments, in the formats:

``--arg``
    Boolean true

``--no-arg``
    Boolean false

``--arg=val``
    A string or numeric value

``--myapp:myarg=val``
    Set the ``myarg`` setting for the ``myapp`` setting.


Arguments names are not case sensitive on the command line, but we recommend
you use lowercase for clarity and consistency with code.


Core arguments
~~~~~~~~~~~~~~

Core arguments use the namespace ``sermin``, but that is optional (ie ``--dry``
and ``--sermin:dry`` are equivalent).

``--source=<source>``
    The source that contains the blueprint - see
    :ref:`specifying_a_blueprint` for more details

.. TODO: add --settings

``--settings=<path>``

    Path to settings file. See :ref:`settings_file` for details.

    Options set in the settings file will be overridden by command
    line arguments.

    If no settings file is provided, Sermin will check the current path for
    ``sermin-settings.py``, before falling back to hard-coded defaults.

    Default: ``sermin-settings.py``

.. TODO: add --host support

``--host=[<user>[:<key path>]@]<host>[:<ssh port>]``
    Apply the state to the host, using SSH.

    This argument can be provided more than once, to target multiple hosts.

    Default: None

.. TODO: add reporting

``--dry``
    Check the state, but make no changes

    Default: Off (apply changes)

``--verbosity``
    Reporting verbosity. One of:

    ``debug``
        Explain decisions Sermin takes (the ``check`` phase)

    ``info``
        Show what Sermin is doing (the ``apply`` phase)

    ``warning``
        Show warnings for problems Sermin can ignore

    ``error``
        Show errors that Sermin can't ignore


Host arguments
~~~~~~~~~~~~~~

Host arguments provide defaults for each host. If the host is not
configured to run Sermin, it will be configured using these settings.

These settings can also be set on a per-host basis in a `Host` object in a
:ref:`settings_file`.

.. TODO: --sermin

``--sermin=<path>``, ``--sermin=<path>``
    The path to the Sermin installation. This will normally be a virtualenv.
    If not found, it will be installed.

    Default: /usr/local/sermin

.. TODO: --python

``--python=<path>``
    The python command. If not found, it will be installed.

.. TODO: --virtualenv

``--virtualenv=<path>``
    The virtualenv command. If not found, it will be installed.

.. TODO: --pip

``--pip=<path>``
    The pip command. If not found, it will be installed.


.. _settings_file:

Settings file
-------------

Arguments can be stored in a settings file - a Python script which defines
arguments in namespaces for the module they are configuring. Core
arguments are defined in the ``sermin`` namespace.

Settings are overridden by command line arguments.

As on the command line, settings are not case sensitive; follow Python
standards for clarity.

An example settings file::

    from sermin import Host

    class Sermin:
        # --dry
        dry = True

        # --host=user:path/to/ssh.key@foo.example.com
        # --host=user:path/to/ssh.key@bar.example.com
        host = [
            Host('foo.example.com', username='user', key='path/to/ssh.key'),
            Host('bar.example.com', username='user', key='path/to/ssh.key'),
        ]

    class MyApp:
        # --myapp:myarg=True
        myarg = True
