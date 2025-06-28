gaussdb: GaussDB database adapter for Python
=================================================

gaussdb is a modern implementation of a GaussDB adapter for Python.

This distribution contains the pure Python package ``gaussdb``.

.. Note::

    Despite the lack of number in the package name, this package is the
    successor of psycopg2.

    Please use the _GaussDB package if you are maintaining an existing program
    using _GaussDB as a dependency. If you are developing something new,
    gaussdb is the most current implementation of the adapter.



Installation
------------

In short, run the following::

    pip install --upgrade pip           # to upgrade pip
    pip install "gaussdb[dev,pool]"  # to install package and dependencies

If something goes wrong, and for more information about installation, please
check out the `Installation documentation`.


Hacking
-------

For development information check out `the project readme`.


Copyright (C) 2020 The Psycopg Team
