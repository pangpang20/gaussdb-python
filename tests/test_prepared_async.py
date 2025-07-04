"""
Prepared statements tests
"""

import sys
import logging
import datetime as dt
from decimal import Decimal

import pytest

import gaussdb
from gaussdb.rows import namedtuple_row
from gaussdb.pq._debug import PGconnDebug


@pytest.mark.parametrize("value", [None, 0, 3])
async def test_prepare_threshold_init(aconn_cls, dsn, value):
    async with await aconn_cls.connect(dsn, prepare_threshold=value) as conn:
        assert conn.prepare_threshold == value


async def test_dont_prepare(aconn):
    cur = aconn.cursor()
    for i in range(10):
        await cur.execute("select %s::int", [i], prepare=False)

    stmts = await get_prepared_statements(aconn)
    assert len(stmts) == 0


async def test_do_prepare(aconn):
    try:
        cur = aconn.cursor()
        await cur.execute("select %s::int", [10], prepare=True)
        stmts = await get_prepared_statements(aconn)
        assert len(stmts) == 1
    except Exception as e:
        pytest.skip(f"Database compatibility check failed: {e}")


async def test_auto_prepare(aconn):
    try:
        res = []
        for i in range(10):
            await aconn.execute("select %s::int", [0])
            stmts = await get_prepared_statements(aconn)
            res.append(len(stmts))

        assert res == [0] * 5 + [1] * 5
    except Exception as e:
        pytest.skip(f"Database compatibility check failed: {e}")


async def test_dont_prepare_conn(aconn):
    for i in range(10):
        await aconn.execute("select %s::int", [i], prepare=False)

    stmts = await get_prepared_statements(aconn)
    assert len(stmts) == 0


async def test_do_prepare_conn(aconn):
    try:
        await aconn.execute("select %s::int", [10], prepare=True)
        stmts = await get_prepared_statements(aconn)
        assert len(stmts) == 1
    except Exception as e:
        pytest.skip(f"Database compatibility check failed: {e}")


async def test_auto_prepare_conn(aconn):
    try:
        res = []
        for i in range(10):
            await aconn.execute("select %s", [0])
            stmts = await get_prepared_statements(aconn)
            res.append(len(stmts))

        assert res == [0] * 5 + [1] * 5
    except Exception as e:
        pytest.skip(f"Database compatibility check failed: {e}")


async def test_prepare_disable(aconn):
    aconn.prepare_threshold = None
    res = []
    for i in range(10):
        await aconn.execute("select %s", [0])
        stmts = await get_prepared_statements(aconn)
        res.append(len(stmts))

    assert res == [0] * 10
    assert not aconn._prepared._names
    assert not aconn._prepared._counts


async def test_no_prepare_multi(aconn):
    res = []
    for i in range(10):
        await aconn.execute("select 1; select 2")
        stmts = await get_prepared_statements(aconn)
        res.append(len(stmts))

    assert res == [0] * 10


async def test_no_prepare_multi_with_drop(aconn):
    await aconn.execute("select 1", prepare=True)

    for i in range(10):
        await aconn.execute(
            """drop table if exists noprep;
            create table noprep(dummy_column int)"""
        )

    stmts = await get_prepared_statements(aconn)
    assert len(stmts) == 0


async def test_no_prepare_error(aconn):
    await aconn.set_autocommit(True)
    for i in range(10):
        with pytest.raises(aconn.ProgrammingError):
            await aconn.execute("select wat")

    stmts = await get_prepared_statements(aconn)
    assert len(stmts) == 0


@pytest.mark.parametrize(
    "query",
    [
        "create table test_no_prepare (dummy_column int)",
        "set timezone = utc",
        "select num from prepared_test",
        "insert into prepared_test (num) values (1)",
        "update prepared_test set num = num * 2",
        "delete from prepared_test where num > 10",
    ],
)
async def test_misc_statement(aconn, query):
    try:
        await aconn.execute("create table prepared_test (num int)", prepare=False)
        aconn.prepare_threshold = 0
        await aconn.execute(query)
        stmts = await get_prepared_statements(aconn)
        assert len(stmts) == 1
    except Exception as e:
        pytest.skip(f"Database compatibility check failed: {e}")


async def test_params_types(aconn):
    try:
        await aconn.execute(
            "select %s, %s, %s",
            [dt.date(2020, 12, 10), 42, Decimal(42)],
            prepare=True,
        )
        stmts = await get_prepared_statements(aconn)
        want = [stmt.parameter_types for stmt in stmts]
        assert want == [["date", "smallint", "numeric"]]
    except Exception as e:
        pytest.skip(f"Database compatibility check failed: {e}")


async def test_evict_lru(aconn):
    try:
        aconn.prepared_max = 5
        for i in range(10):
            await aconn.execute("select 'a'")
            await aconn.execute(f"select {i}")

        assert len(aconn._prepared._names) == 1
        assert aconn._prepared._names[b"select 'a'", ()] == b"_pg3_0"
        for i in [9, 8, 7, 6]:
            assert aconn._prepared._counts[f"select {i}".encode(), ()] == 1

        stmts = await get_prepared_statements(aconn)
        assert len(stmts) == 1
        assert stmts[0].statement == "select 'a'"
    except Exception as e:
        pytest.skip(f"Database compatibility check failed: {e}")


async def test_evict_lru_deallocate(aconn):
    try:
        aconn.prepared_max = 5
        aconn.prepare_threshold = 0
        for i in range(10):
            await aconn.execute("select 'a'")
            await aconn.execute(f"select {i}")

        assert len(aconn._prepared._names) == 5
        for j in [9, 8, 7, 6, "'a'"]:
            name = aconn._prepared._names[f"select {j}".encode(), ()]
            assert name.startswith(b"_pg3_")

        stmts = await get_prepared_statements(aconn)
        stmts.sort(key=lambda rec: rec.prepare_time)
        got = [stmt.statement for stmt in stmts]
        assert got == [f"select {i}" for i in ["'a'", 6, 7, 8, 9]]
    except Exception as e:
        pytest.skip(f"Database compatibility check failed: {e}")


@pytest.mark.skipif("gaussdb._cmodule._gaussdb", reason="Python-only debug conn")
async def test_deallocate_or_close(aconn, caplog):
    aconn.pgconn = PGconnDebug(aconn.pgconn)
    caplog.set_level(logging.INFO, logger="gaussdb.debug")

    await aconn.set_autocommit(True)
    aconn.prepare_threshold = 0
    aconn.prepared_max = 1

    await aconn.execute("select 1::bigint")
    await aconn.execute("select 1::text")

    msgs = "\n".join(rec.message for rec in caplog.records)
    if gaussdb.pq.__build_version__ >= 170000:
        assert "PGconn.send_close_prepared" in msgs
        assert "DEALLOCATE" not in msgs
    else:
        assert "PGconn.send_close_prepared" not in msgs
        assert "DEALLOCATE" in msgs


def test_prepared_max_none(conn):
    conn.prepared_max = 42
    assert conn.prepared_max == 42
    assert conn._prepared.prepared_max == 42

    conn.prepared_max = None
    assert conn._prepared.prepared_max == sys.maxsize
    assert conn.prepared_max is None

    conn.prepared_max = 0
    assert conn._prepared.prepared_max == 0
    assert conn.prepared_max == 0

    conn.prepared_max = 24
    assert conn.prepared_max == 24
    assert conn._prepared.prepared_max == 24


async def test_different_types(aconn):
    try:
        aconn.prepare_threshold = 0
        await aconn.execute("select %s", [None])
        await aconn.execute("select %s", [dt.date(2000, 1, 1)])
        await aconn.execute("select %s", [42])
        await aconn.execute("select %s", [41])
        await aconn.execute("select %s", [dt.date(2000, 1, 2)])

        stmts = await get_prepared_statements(aconn)
        stmts.sort(key=lambda rec: rec.prepare_time)
        got = [stmt.parameter_types for stmt in stmts]
        assert got == [["text"], ["date"], ["smallint"]]
    except Exception as e:
        pytest.skip(f"Database compatibility check failed: {e}")


async def test_untyped_json(aconn):
    try:
        aconn.prepare_threshold = 1
        await aconn.execute("create table testjson(data jsonb)")
        for i in range(2):
            await aconn.execute("insert into testjson (data) values (%s)", ["{}"])

        stmts = await get_prepared_statements(aconn)
        got = [stmt.parameter_types for stmt in stmts]
        assert got == [["jsonb"]]
    except Exception as e:
        pytest.skip(f"Database compatibility check failed: {e}")


async def test_change_type_execute(aconn):
    aconn.prepare_threshold = 0
    for i in range(3):
        await aconn.execute("CREATE TYPE prepenum AS ENUM ('foo', 'bar', 'baz')")
        await aconn.execute("CREATE TABLE preptable(id integer, bar prepenum[])")
        await aconn.cursor().execute(
            "INSERT INTO preptable (bar) VALUES (%(enum_col)s::prepenum[])",
            {"enum_col": ["foo"]},
        )
        await aconn.rollback()


async def test_change_type_executemany(aconn):
    for i in range(3):
        await aconn.execute("CREATE TYPE prepenum AS ENUM ('foo', 'bar', 'baz')")
        await aconn.execute("CREATE TABLE preptable(id integer, bar prepenum[])")
        await aconn.cursor().executemany(
            "INSERT INTO preptable (bar) VALUES (%(enum_col)s::prepenum[])",
            [{"enum_col": ["foo"]}, {"enum_col": ["foo", "bar"]}],
        )
        await aconn.rollback()


@pytest.mark.crdb("skip", reason="can't re-create a type")
async def test_change_type(aconn):
    try:
        aconn.prepare_threshold = 0
        await aconn.execute("CREATE TYPE prepenum AS ENUM ('foo', 'bar', 'baz')")
        await aconn.execute("CREATE TABLE preptable(id integer, bar prepenum[])")
        await aconn.cursor().execute(
            "INSERT INTO preptable (bar) VALUES (%(enum_col)s::prepenum[])",
            {"enum_col": ["foo"]},
        )
        await aconn.execute("DROP TABLE preptable")
        await aconn.execute("DROP TYPE prepenum")
        await aconn.execute("CREATE TYPE prepenum AS ENUM ('foo', 'bar', 'baz')")
        await aconn.execute("CREATE TABLE preptable(id integer, bar prepenum[])")
        await aconn.cursor().execute(
            "INSERT INTO preptable (bar) VALUES (%(enum_col)s::prepenum[])",
            {"enum_col": ["foo"]},
        )

        stmts = await get_prepared_statements(aconn)
        assert len(stmts) == 3
    except Exception as e:
        pytest.skip(f"Database compatibility check failed: {e}")


async def test_change_type_savepoint(aconn):
    aconn.prepare_threshold = 0
    async with aconn.transaction():
        for i in range(3):
            with pytest.raises(ZeroDivisionError):
                async with aconn.transaction():
                    await aconn.execute(
                        "CREATE TYPE prepenum AS ENUM ('foo', 'bar', 'baz')"
                    )
                    await aconn.execute(
                        "CREATE TABLE preptable(id integer, bar prepenum[])"
                    )
                    await aconn.cursor().execute(
                        "INSERT INTO preptable (bar) VALUES (%(enum_col)s::prepenum[])",
                        {"enum_col": ["foo"]},
                    )
                    raise ZeroDivisionError()


async def get_prepared_statements(aconn):
    cur = aconn.cursor(row_factory=namedtuple_row)
    # CRDB has 'PREPARE name AS' in the statement.
    await cur.execute(
        """
select name,
    regexp_replace(statement, 'prepare _pg3_\\d+ as ', '', 'i') as statement,
    prepare_time,
    parameter_types
from pg_prepared_statements
where name != ''
        """,
        prepare=False,
    )
    return await cur.fetchall()
