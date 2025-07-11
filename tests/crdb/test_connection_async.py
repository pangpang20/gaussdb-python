import time

import pytest

import gaussdb.crdb
from gaussdb import errors as e
from gaussdb.crdb import AsyncCrdbConnection

from ..acompat import asleep, gather, spawn

pytestmark = [pytest.mark.crdb]
if True:  # ASYNC
    pytestmark.append(pytest.mark.anyio)


async def test_is_crdb(aconn):
    assert AsyncCrdbConnection.is_crdb(aconn)
    assert AsyncCrdbConnection.is_crdb(aconn.pgconn)


async def test_connect(dsn):
    async with await AsyncCrdbConnection.connect(dsn) as conn:
        assert isinstance(conn, AsyncCrdbConnection)

    if False:  # ASYNC
        with gaussdb.crdb.connect(dsn) as conn:
            assert isinstance(conn, AsyncCrdbConnection)


async def test_xid(dsn):
    async with await AsyncCrdbConnection.connect(dsn) as conn:
        with pytest.raises(e.NotSupportedError):
            conn.xid(1, "gtrid", "bqual")


async def test_tpc_begin(dsn):
    async with await AsyncCrdbConnection.connect(dsn) as conn:
        with pytest.raises(e.NotSupportedError):
            await conn.tpc_begin("foo")


async def test_tpc_recover(dsn):
    async with await AsyncCrdbConnection.connect(dsn) as conn:
        with pytest.raises(e.NotSupportedError):
            await conn.tpc_recover()


@pytest.mark.slow
async def test_broken_connection(aconn):
    cur = aconn.cursor()
    await cur.execute("select session_id from [show session_id]")
    (session_id,) = await cur.fetchone()
    with pytest.raises(gaussdb.DatabaseError):
        await cur.execute("cancel session %s", [session_id])
    assert aconn.closed


@pytest.mark.slow
async def test_broken(aconn):
    cur = await aconn.execute("show session_id")
    (session_id,) = await cur.fetchone()
    with pytest.raises(gaussdb.OperationalError):
        await aconn.execute("cancel session %s", [session_id])

    assert aconn.closed
    assert aconn.broken
    await aconn.close()
    assert aconn.closed
    assert aconn.broken


@pytest.mark.slow
@pytest.mark.timing
async def test_identify_closure(aconn_cls, dsn):
    async with await aconn_cls.connect(dsn, autocommit=True) as conn:
        async with await aconn_cls.connect(dsn, autocommit=True) as conn2:
            cur = await conn.execute("show session_id")
            (session_id,) = await cur.fetchone()

            async def closer():
                await asleep(0.2)
                await conn2.execute("cancel session %s", [session_id])

            t = spawn(closer)
            t0 = time.time()
            try:
                with pytest.raises(gaussdb.OperationalError):
                    await conn.execute("select pg_sleep(3.0)")
                dt = time.time() - t0
                # CRDB seems to take not less than 1s
                assert 0.2 < dt < 2
            finally:
                await gather(t)
