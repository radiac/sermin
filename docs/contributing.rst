============
Contributing
============

Contributions are welcome, preferably via pull request. Check the github issues
and project :ref:`roadmap <roadmap>` to see what needs work.

If you have a state class or module that you think would be a good addition to
the core states, please raise an issue to discuss it before submitting a PR.
Core states are usually reserved for very general operations; if your state is
specific to a platform, application or service, it's probably more suited to
the contrib states, or being released independently.


Installing
==========

The easiest way to work on Sermin is to fork the project on github, then
install it to a virtualenv::

    virtualenv sermin
    cd sermin
    source bin/activate
    pip install -e git+git@github.com:USERNAME/sermin.git#egg=sermin[dev]

(replacing ``USERNAME`` with your username).

This will also install all the dependencies you need for development and
testing; you'll find the Sermin source ready for you to work on in the
``src`` folder of your virtualenv.


Testing
=======

It is greatly appreciated when contributions come with tests. Patches which
lack tests (or do not pass) are unlikely to be merged in a timely manner.

The Sermin tests are in the ``tests`` folder.


Test modes
----------

Tests can be run in two modes:

* ``safe`` (default) - code unit tests, no changes will be made to the system.
  This mode is safe to run on your development machine; state tests will be
  skipped. This mode primarily exists for people who are too busy to read these
  instructions and run tests properly in a VM.
* ``full`` (default for Vagrant) - integration tests which check and apply
  states. Because this makes changes to your packages, services and file
  system, it is strongly advised that you run this in a disposable virtual
  machine with Vagrant.

When adding tests, be sure to check whether you're adding them to a
``SafeTestCase`` or ``FullTestCase`` subclass, and whether that makes sense for
your tests.


Running safe tests locally
--------------------------

To run the tests with debug data::

    cd src/sermin
    nosetests -s -vv

To run the tests without debug data::

    python setup.py test

Use tox to run them on one or more supported versions::

    tox [-e py27] [tests[.test_module.TestClass]]

Tox will also generate a coverage HTML report.

You could use ``detox`` to run the tests concurrently, but you will need to run
``tox -e report`` afterwards to generate the coverage report. Because the tests
modify the system, you can only use ``detox`` in ``safe`` mode.


Running full tests with Vagrant
-------------------------------

First install vagrant (eg ``apt install virtualbox vagrant``, or follow the
`official instructions <https://www.vagrantup.com/docs/installation/>`_).

Provision and start your Vagrant machine with::

    vagrant up --provision

Run tests::

    python setup.py vagrant

Alternatively you can `vagrant ssh` and run the tests manually::

    source venv/bin/activate
    cd source
    flake8
    SERMIN_TEST_MODE=full python setup.py test
    # or: SERMIN_TEST_MODE=full tox

Stop your Vagrant machine after testing::

    vagrant halt

If everything goes wrong, destroy your Vagrant machine with::

    vagrant destroy


Documentation
=============

This documentation is built using sphinx, and is available online.

If you want to build the documentation locally, move to the ``docs`` directory
and run ``make html``.


Code overview
=============

The Sermin command in ``bin/sermin`` calls ``sermin.runner``, which creates a
``Sermin`` instance that parses the command line arguments and initialises
settings, and then loads and runs the specified script or connects to the host.

When a State is defined in a script, it is added to the global
``sermin.state.base.registry.registry`` registry. The runner then calls the
``registry.check`` and ``registry.apply`` methods, which in turn call the
states' ``check`` and ``apply`` methods.


.. _roadmap:

Roadmap
=======

0.1
---

* ``Git`` state logging and tests
* ``User`` and ``Group`` states
* Ownership and permission management for ``Dir`` and ``File`` states
* Host arguments for deploying to remote hosts
* Complete planned command line options


0.2
---

* Test support in ``State`` for post-apply checks
* Snapshot support in ``State`` for rollback
* Test with Python 3.2+


0.3
---

