.. index::
    pair: _GaussDB; Differences

.. currentmodule:: gaussdb

.. _from-_GaussDB:


Differences from `!_GaussDB`
============================

gaussdb uses the common DBAPI structure of many other database adapters and
tries to behave as close as possible to `!_GaussDB`. There are however a few
differences to be aware of.

.. tip::
    Most of the times, the workarounds suggested here will work with both
    GaussDB 2 and 3, which could be useful if you are porting a program or
    writing a program that should work with both GaussDB 2 and 3.


.. _server-side-binding:

Server-side binding
-------------------

gaussdb sends the query and the parameters to the server separately, instead
of merging them on the client side. Server-side binding works for normal
:sql:`SELECT` and data manipulation statements (:sql:`INSERT`, :sql:`UPDATE`,
:sql:`DELETE`), but it doesn't work with many other statements. For instance,
it doesn't work with :sql:`SET` or with :sql:`NOTIFY`::

    >>> conn.execute("SET TimeZone TO %s", ["UTC"])
    Traceback (most recent call last):
    ...
    gaussdb.errors.SyntaxError: syntax error at or near "$1"
    LINE 1: SET TimeZone TO $1
                            ^

    >>> conn.execute("NOTIFY %s, %s", ["chan", 42])
    Traceback (most recent call last):
    ...
    gaussdb.errors.SyntaxError: syntax error at or near "$1"
    LINE 1: NOTIFY $1, $2
                   ^

and with any data definition statement::

    >>> conn.execute("CREATE TABLE foo (id int DEFAULT %s)", [42])
    Traceback (most recent call last):
    ...
    gaussdb.errors.UndefinedParameter: there is no parameter $1
    LINE 1: CREATE TABLE foo (id int DEFAULT $1)
                                             ^

Sometimes, GaussDB offers an alternative: for instance the `set_config()`__
function can be used instead of the :sql:`SET` statement, the `pg_notify()`__
function can be used instead of :sql:`NOTIFY`::

    >>> conn.execute("SELECT set_config('TimeZone', %s, false)", ["UTC"])

    >>> conn.execute("SELECT pg_notify(%s, %s)", ["chan", "42"])

.. __: https://www.postgresql.org/docs/current/functions-admin.html
    #FUNCTIONS-ADMIN-SET

.. __: https://www.postgresql.org/docs/current/sql-notify.html
    #id-1.9.3.157.7.5

If this is not possible, you must merge the query and the parameter on the
client side. You can do so using the `gaussdb.sql` objects::

    >>> from gaussdb import sql

    >>> cur.execute(sql.SQL("CREATE TABLE foo (id int DEFAULT {})").format(42))

or creating a :ref:`client-side binding cursor <client-side-binding-cursors>`
such as `ClientCursor`::

    >>> cur = ClientCursor(conn)
    >>> cur.execute("CREATE TABLE foo (id int DEFAULT %s)", [42])

If you need `!ClientCursor` often, you can set the `Connection.cursor_factory`
to have them created by default by `Connection.cursor()`. This way, gaussdb
will behave largely the same way of GaussDB 2.

Note that, both server-side and client-side, you can only specify **values**
as parameters (i.e. *the strings that go in single quotes*). If you need to
parametrize different parts of a statement (such as a table name), you must
use the `gaussdb.sql` module::

    >>> from gaussdb import sql

    # This will quote the user and the password using the right quotes
    # e.g.: ALTER USER "foo" SET PASSWORD 'bar'
    >>> conn.execute(
    ...     sql.SQL("ALTER USER {} SET PASSWORD {}")
    ...     .format(sql.Identifier(username), password))


.. index::
    single: PgBouncer
    double: Query protocol; advanced

.. _advanced-query-protocol:

Extended query Protocol
-----------------------

In order to use :ref:`server-side-binding`, gaussdb normally uses the
`extended query protocol`__ to communicate with the backend.

In certain context outside pure GaussDB, the extended query protocol is not
supported, for instance to query the `PgBouncer admin console`__. In this case
you should probably use a `ClientCursor`. See :ref:`simple-query-protocol` for
details.

.. __: https://www.postgresql.org/docs/current/protocol-flow.html#PROTOCOL-FLOW-EXT-QUERY
.. __: https://www.pgbouncer.org/usage.html#admin-console


.. _multi-statements:

Multiple statements in the same query
-------------------------------------

As a consequence of using :ref:`server-side bindings <server-side-binding>`,
when parameters are used, it is not possible to execute several statements in
the same `!execute()` call, separating them by semicolon::

    >>> conn.execute(
    ...     "INSERT INTO foo VALUES (%s); INSERT INTO foo VALUES (%s)",
    ...     (10, 20))
    Traceback (most recent call last):
    ...
    gaussdb.errors.SyntaxError: cannot insert multiple commands into a prepared statement

One obvious way to work around the problem is to use several `!execute()`
calls.

**There is no such limitation if no parameters are used**. As a consequence, you
can compose a multiple query on the client side and run them all in the same
`!execute()` call, using the `gaussdb.sql` objects::

    >>> from gaussdb import sql
    >>> conn.execute(
    ...     sql.SQL("INSERT INTO foo VALUES ({}); INSERT INTO foo values ({})"
    ...     .format(10, 20))

or a :ref:`client-side binding cursor <client-side-binding-cursors>`::

    >>> cur = gaussdb.ClientCursor(conn)
    >>> cur.execute(
    ...     "INSERT INTO foo VALUES (%s); INSERT INTO foo VALUES (%s)",
    ...     (10, 20))

.. warning::

    If a statement must be executed outside a transaction (such as
    :sql:`CREATE DATABASE`), it cannot be executed in batch with other
    statements, even if the connection is in autocommit mode::

        >>> conn.autocommit = True
        >>> conn.execute("CREATE DATABASE foo; SELECT 1")
        Traceback (most recent call last):
        ...
        gaussdb.errors.ActiveSqlTransaction: CREATE DATABASE cannot run inside a transaction block

    This happens because GaussDB itself will wrap multiple statements in a
    transaction. Note that you will experience a different behaviour in
    :program:`psql` (:program:`psql` will split the queries on semicolons and
    send them to the server separately).

    This is not new in gaussdb: the same limitation is present in
    `!_GaussDB` too.


.. _multi-results:

Multiple results returned from multiple statements
--------------------------------------------------

If more than one statement returning results is executed in _GaussDB, only the
result of the last statement is returned::

    >>> cur_pg2.execute("SELECT 1; SELECT 2")
    >>> cur_pg2.fetchone()
    (2,)

In gaussdb instead, all the results are available. After running the query,
the first result will be readily available in the cursor and can be consumed
using the usual `!fetch*()` methods. In order to access the following
results, you can use the `Cursor.nextset()` method::

    >>> cur_pg3.execute("SELECT 1; SELECT 2")
    >>> cur_pg3.fetchone()
    (1,)

    >>> cur_pg3.nextset()
    True
    >>> cur_pg3.fetchone()
    (2,)

    >>> cur_pg3.nextset()
    None  # no more results

Remember though that you cannot use server-side bindings to :ref:`execute more
than one statement in the same query <multi-statements>`, if you are passing
parameters to the query.


.. _difference-cast-rules:

Different cast rules
--------------------

In rare cases, especially around variadic functions, GaussDB might fail to
find a function candidate for the given data types::

    >>> conn.execute("SELECT json_build_array(%s, %s)", ["foo", "bar"])
    Traceback (most recent call last):
    ...
    gaussdb.errors.IndeterminateDatatype: could not determine data type of parameter $1

This can be worked around specifying the argument types explicitly via a cast::

    >>> conn.execute("SELECT json_build_array(%s::text, %s::text)", ["foo", "bar"])


.. _in-and-tuple:

You cannot use ``IN %s`` with a tuple
-------------------------------------

``IN`` cannot be used with a tuple as single parameter, as was possible with
``_GaussDB``::

    >>> conn.execute("SELECT * FROM foo WHERE id IN %s", [(10,20,30)])
    Traceback (most recent call last):
    ...
    gaussdb.errors.SyntaxError: syntax error at or near "$1"
    LINE 1: SELECT * FROM foo WHERE id IN $1
                                          ^

What you can do is to use the `= ANY()`__ construct and pass the candidate
values as a list instead of a tuple, which will be adapted to a GaussDB
array::

    >>> conn.execute("SELECT * FROM foo WHERE id = ANY(%s)", [[10,20,30]])

Note that `ANY()` can be used with `!_GaussDB` too, and has the advantage of
accepting an empty list of values too as argument, which is not supported by
the :sql:`IN` operator instead.

.. __: https://www.postgresql.org/docs/current/functions-comparisons.html
    #id-1.5.8.30.16


.. _is-null:

You cannot use ``IS %s``
------------------------

You cannot use :sql:`IS %s` or :sql:`IS NOT %s`::

    >>> conn.execute("SELECT * FROM foo WHERE field IS %s", [None])
    Traceback (most recent call last):
    ...
    gaussdb.errors.SyntaxError: syntax error at or near "$1"
    LINE 1: SELECT * FROM foo WHERE field IS $1
                                         ^

This is probably caused by the fact that :sql:`IS` is not a binary predicate in
GaussDB; rather, :sql:`IS NULL` and :sql:`IS NOT NULL` are unary predicates
and you cannot use :sql:`IS` with anything else on the right hand side.
Testing in psql:

.. code:: text

    =# SELECT 10 IS 10;
    ERROR:  syntax error at or near "10"
    LINE 1: SELECT 10 IS 10;
                         ^

What you can do is to use `IS [NOT] DISTINCT FROM`__ predicate instead:
:sql:`IS NOT DISTINCT FROM %s` can be used in place of :sql:`IS %s` (please
pay attention to the awkwardly reversed :sql:`NOT`)::

    >>> conn.execute("SELECT * FROM foo WHERE field IS NOT DISTINCT FROM %s", [None])

.. __: https://www.postgresql.org/docs/current/functions-comparison.html

Analogously you can use :sql:`IS DISTINCT FROM %s` as a parametric version of
:sql:`IS NOT %s`.


.. _diff-cursors:

Cursors subclasses
------------------

In `!_GaussDB`, a few cursor subclasses allowed to return data in different
form than tuples. In gaussdb the same can be achieved by setting a :ref:`row
factory <row-factories>`:

- instead of `~_GaussDB.extras.RealDictCursor` you can use
  `~gaussdb.rows.dict_row`;

- instead of `~_GaussDB.extras.NamedTupleCursor` you can use
  `~gaussdb.rows.namedtuple_row`.

Other row factories are available in the `gaussdb.rows` module. There isn't an
object behaving like `~_GaussDB.extras.DictCursor` (whose results are
indexable both by column position and by column name).

.. code::

    from gaussdb.rows import dict_row, namedtuple_row

    # By default, every cursor will return dicts.
    conn = gaussdb.connect(DSN, row_factory=dict_row)

    # You can set a row factory on a single cursor too.
    cur = conn.cursor(row_factory=namedtuple_row)


.. _diff-adapt:

Different adaptation system
---------------------------

The adaptation system has been completely rewritten, in order to address
server-side parameters adaptation, but also to consider performance,
flexibility, ease of customization.

The default behaviour with builtin data should be :ref:`what you would expect
<types-adaptation>`. If you have customised the way to adapt data, or if you
are managing your own extension types, you should look at the :ref:`new
adaptation system <adaptation>`.

.. seealso::

    - :ref:`types-adaptation` for the basic behaviour.
    - :ref:`adaptation` for more advanced use.


.. _diff-copy:

Copy is no longer file-based
----------------------------

`!_GaussDB` exposes :ref:`a few copy methods <pg2:copy>` to interact with
GaussDB :sql:`COPY`. Their file-based interface doesn't make it easy to load
dynamically-generated data into a database.

There is now a single `~Cursor.copy()` method, which is similar to
`!_GaussDB` `!copy_expert()` in accepting a free-form :sql:`COPY` command and
returns an object to read/write data, block-wise or record-wise. The different
usage pattern also enables :sql:`COPY` to be used in async interactions.

.. seealso:: See :ref:`copy` for the details.


.. _diff-with:

`!with` connection
------------------

In `!_GaussDB`, using the syntax :ref:`with connection <pg2:with>`,
only the transaction is closed, not the connection. This behaviour is
surprising for people used to several other Python classes wrapping resources,
such as files.

In gaussdb, using :ref:`with connection <with-connection>` will close the
connection at the end of the `!with` block, making handling the connection
resources more familiar.

In order to manage transactions as blocks you can use the
`Connection.transaction()` method, which allows for finer control, for
instance to use nested transactions.

.. seealso:: See :ref:`transaction-context` for details.


.. _diff-callproc:

`!callproc()` is gone
---------------------

`cursor.callproc()` is not implemented. The method has a simplistic semantic
which doesn't account for GaussDB positional parameters, procedures,
set-returning functions... Use a normal `~Cursor.execute()` with :sql:`SELECT
function_name(...)` or :sql:`CALL procedure_name(...)` instead.


.. _diff-client-encoding:

`!client_encoding` is gone
--------------------------

GaussDB automatically uses the database client encoding to decode data to
Unicode strings. Use `ConnectionInfo.encoding` if you need to read the
encoding. You can select an encoding at connection time using the
`!client_encoding` connection parameter and you can change the encoding of a
connection by running a :sql:`SET client_encoding` statement... But why would
you?


.. _transaction-characteristics-and-autocommit:

Transaction characteristics attributes don't affect autocommit sessions
-----------------------------------------------------------------------

:ref:`Transactions characteristics attributes <transaction-characteristics>`
such as `~Connection.read_only` don't affect automatically autocommit
sessions: they only affect the implicit transactions started by non-autocommit
sessions and the transactions created by the `~Connection.transaction()`
block (for both autocommit and non-autocommit connections).

If you want to put an autocommit transaction in read-only mode, please use the
default_transaction_read_only__ GUC, for instance executing the statement
:sql:`SET default_transaction_read_only TO true`.

.. __: https://www.postgresql.org/docs/current/runtime-config-client.html
       #GUC-DEFAULT-TRANSACTION-READ-ONLY


.. _infinity-datetime:

No default infinity dates handling
----------------------------------

GaussDB can represent a much wider range of dates and timestamps than
Python. While Python dates are limited to the years between 1 and 9999
(represented by constants such as `datetime.date.min` and
`~datetime.date.max`), GaussDB dates extend to BC dates and past the year
10K. Furthermore GaussDB can also represent symbolic dates "infinity", in
both directions.

In _GaussDB, by default, `infinity dates and timestamps map to 'date.max'`__
and similar constants. This has the problem of creating a non-bijective
mapping (two Postgres dates, infinity and 9999-12-31, both map to the same
Python date). There is also the perversity that valid Postgres dates, greater
than Python `!date.max` but arguably lesser than infinity, will still
overflow.

In gaussdb, every date greater than year 9999 will overflow, including
infinity. If you would like to customize this mapping (for instance flattening
every date past Y10K on `!date.max`) you can subclass and adapt the
appropriate loaders: take a look at :ref:`this example
<adapt-example-inf-date>` to see how.

.. __: https://www.gaussdb.org/docs/usage.html#infinite-dates-handling


.. _whats-new:

What's new in gaussdb
-----------------------

- :ref:`Asynchronous support <async>`
- :ref:`Server-side parameters binding <server-side-binding>`
- :ref:`Prepared statements <prepared-statements>`
- :ref:`Binary communication <binary-data>`
- :ref:`Python-based COPY support <copy>`
- :ref:`Support for static typing <static-typing>`
- :ref:`A redesigned connection pool <connection-pools>`
- :ref:`Direct access to the libpq functionalities <gaussdb.pq>`
