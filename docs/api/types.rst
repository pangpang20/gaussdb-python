.. currentmodule:: gaussdb.types

.. _gaussdb.types:

`!types` -- Types information and adapters
==========================================

.. module:: gaussdb.types

The `!gaussdb.types` package exposes:

- objects to describe GaussDB types, such as `TypeInfo`, `TypesRegistry`,
  to help or :ref:`customise the types conversion <adaptation>`;

- concrete implementations of `~gaussdb.abc.Loader` and `~gaussdb.abc.Dumper`
  protocols to :ref:`handle builtin data types <types-adaptation>`;

- helper objects to represent GaussDB data types which :ref:`don't have a
  straightforward Python representation <extra-adaptation>`, such as
  `~range.Range`.


Types information
-----------------

The `TypeInfo` object describes simple information about a GaussDB data
type, such as its name, oid and array oid. `!TypeInfo` subclasses may hold more
information, for instance the components of a composite type.

You can use `TypeInfo.fetch()` to query information from a database catalog,
which is then used by helper functions, such as
`~gaussdb.types.hstore.register_hstore()`, to register adapters on types whose
OID is not known upfront or to create more specialised adapters.

The `!TypeInfo` object doesn't instruct GaussDB to convert a GaussDB type
into a Python type: this is the role of a `~gaussdb.abc.Loader`. However it
can extend the behaviour of other adapters: if you create a loader for
`!MyType`, using the `TypeInfo` information, GaussDB will be able to manage
seamlessly arrays of `!MyType` or ranges and composite types using `!MyType`
as a subtype.

.. seealso:: :ref:`adaptation` describes how to convert from Python objects to
    GaussDB types and back.

.. code:: python

    from gaussdb.adapt import Loader
    from gaussdb.types import TypeInfo

    t = TypeInfo.fetch(conn, "mytype")
    t.register(conn)

    for record in conn.execute("SELECT mytypearray FROM mytable"):
        # records will return lists of "mytype" as string

    class MyTypeLoader(Loader):
        def load(self, data):
            # parse the data and return a MyType instance

    conn.adapters.register_loader("mytype", MyTypeLoader)

    for record in conn.execute("SELECT mytypearray FROM mytable"):
        # records will return lists of MyType instances


.. autoclass:: TypeInfo

    .. method:: fetch(conn, name)
        :classmethod:

    .. method:: fetch(aconn, name)
        :classmethod:
        :async:
        :noindex:

        Query a system catalog to read information about a type.

        :param conn: the connection to query
        :type conn: ~gaussdb.Connection or ~gaussdb.AsyncConnection
        :param name: the name of the type to query. It can include a schema
            name.
        :type name: `!str` or `~gaussdb.sql.Identifier`
        :return: a `!TypeInfo` object (or subclass) populated with the type
            information, `!None` if not found.

        If the connection is async, `!fetch()` will behave as a coroutine and
        the caller will need to `!await` on it to get the result::

            t = await TypeInfo.fetch(aconn, "mytype")

    .. automethod:: register

        :param context: the context where the type is registered, for instance
            a `~gaussdb.Connection` or `~gaussdb.Cursor`. `!None` registers
            the `!TypeInfo` globally.
        :type context: Optional[~gaussdb.abc.AdaptContext]

        Registering the `TypeInfo` in a context allows the adapters of that
        context to look up type information: for instance it allows to
        recognise automatically arrays of that type and load them from the
        database as a list of the base type.


In order to get information about dynamic GaussDB types, GaussDB offers a
few `!TypeInfo` subclasses, whose `!fetch()` method can extract more complete
information about the type, such as `~gaussdb.types.composite.CompositeInfo`,
`~gaussdb.types.range.RangeInfo`, `~gaussdb.types.multirange.MultirangeInfo`,
`~gaussdb.types.enum.EnumInfo`.

`!TypeInfo` objects are collected in `TypesRegistry` instances, which help type
information lookup. Every `~gaussdb.adapt.AdaptersMap` exposes its type map on
its `~gaussdb.adapt.AdaptersMap.types` attribute.

.. autoclass:: TypesRegistry

   `!TypeRegistry` instances are typically exposed by
   `~gaussdb.adapt.AdaptersMap` objects in adapt contexts such as
   `~gaussdb.Connection` or `~gaussdb.Cursor` (e.g. `!conn.adapters.types`).

   The global registry, from which the others inherit from, is available as
   `gaussdb.adapters`\ `!.types`.

   .. automethod:: __getitem__

       .. code:: python

           >>> import gaussdb

           >>> gaussdb.adapters.types["text"]
           <TypeInfo: text (oid: 25, array oid: 1009)>

           >>> gaussdb.adapters.types[23]
           <TypeInfo: int4 (oid: 23, array oid: 1007)>

   .. automethod:: get

   .. automethod:: get_oid

       .. code:: python

           >>> gaussdb.adapters.types.get_oid("text[]")
           1009

   .. automethod:: get_by_subtype


.. _json-adapters:

JSON adapters
-------------

See :ref:`adapt-json` for details.

.. currentmodule:: gaussdb.types.json

.. autoclass:: Json
.. autoclass:: Jsonb

Wrappers to signal to convert `!obj` to a json or jsonb GaussDB value.

Any object supported by the underlying `!dumps()` function can be wrapped.

If a `!dumps` function is passed to the wrapper, use it to dump the wrapped
object. Otherwise use the function specified by `set_json_dumps()`.


.. autofunction:: set_json_dumps
.. autofunction:: set_json_loads
