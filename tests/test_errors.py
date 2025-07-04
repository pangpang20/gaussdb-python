from __future__ import annotations

import re
import sys
import pickle
from weakref import ref

import pytest

import gaussdb
from gaussdb import errors as e
from gaussdb import pq

from .utils import eur
from .fix_crdb import is_crdb


def test_finishedpgconn(pgconn):
    with pytest.raises(TypeError):
        e.FinishedPGconn.connect()

    assert pgconn.socket
    finished = e.finish_pgconn(pgconn)
    with pytest.raises(e.OperationalError, match="connection is closed"):
        finished.socket
    with pytest.raises(e.OperationalError, match="connection is closed"):
        pgconn.socket


@pytest.mark.crdb_skip("severity_nonlocalized")
def test_error_diag(conn):
    cur = conn.cursor()
    with pytest.raises(e.DatabaseError) as excinfo:
        cur.execute("select 1 from wat")

    exc = excinfo.value
    diag = exc.diag
    assert diag.sqlstate == "42P01"


def test_diag_all_attrs(pgconn):
    res = pgconn.make_empty_result(pq.ExecStatus.NONFATAL_ERROR)
    diag = e.Diagnostic(res)
    for d in pq.DiagnosticField:
        if d == pq.DiagnosticField.SEVERITY_NONLOCALIZED:
            continue
        val = getattr(diag, d.name.lower())
        assert val is None or isinstance(val, str)


def test_diag_right_attr(pgconn, monkeypatch):
    res = pgconn.make_empty_result(pq.ExecStatus.NONFATAL_ERROR)
    diag = e.Diagnostic(res)

    to_check: pq.DiagnosticField
    checked: list[pq.DiagnosticField] = []

    def check_val(self, v):
        assert to_check == v
        checked.append(v)
        return None

    monkeypatch.setattr(e.Diagnostic, "_error_message", check_val)

    for to_check in pq.DiagnosticField:
        if to_check == pq.DiagnosticField.SEVERITY_NONLOCALIZED:
            continue
        getattr(diag, to_check.name.lower())

    assert len(checked) == len(pq.DiagnosticField) - 1


def test_diag_attr_values(conn):
    if is_crdb(conn):
        conn.execute("set experimental_enable_temp_tables = 'on'")
    conn.execute(
        """
        create temp table test_exc (
            data int constraint chk_eq1 check (data = 1)
        )"""
    )
    with pytest.raises(e.Error) as exc:
        conn.execute("insert into test_exc values(2)")
    diag = exc.value.diag
    assert diag.sqlstate == "23514"
    match_obj = re.search(r'constraint "([^"]+)"', diag.message_primary or "")
    assert match_obj is not None
    assert match_obj.group(1) == "chk_eq1"
    match_obj = re.search(r'relation "([^"]+)"', diag.message_primary or "")
    assert match_obj is not None
    assert match_obj.group(1) == "test_exc"


@pytest.mark.crdb_skip("do")
@pytest.mark.parametrize("enc", ["utf8", "latin9"])
def test_diag_encoding(conn, enc):
    msgs = []
    conn.pgconn.exec_(b"set client_min_messages to notice")
    conn.add_notice_handler(lambda diag: msgs.append(diag.message_primary))
    conn.execute(f"set client_encoding to {enc}")
    cur = conn.cursor()
    cur.execute("do $$begin raise notice 'hello %', chr(8364); end$$ language plpgsql")
    assert msgs == [f"hello {eur}"]


@pytest.mark.crdb_skip("do")
@pytest.mark.opengauss_skip("do")
@pytest.mark.parametrize("enc", ["utf8", "latin9"])
def test_error_encoding(conn, enc):
    with conn.transaction():
        conn.execute(f"set client_encoding to {enc}")
    cur = conn.cursor()
    with pytest.raises(e.DatabaseError) as excinfo:
        cur.execute(
            """
            do $$begin
                execute format('insert into "%s" values (1)', chr(8364));
            end$$ language plpgsql;
            """
        )

    diag = excinfo.value.diag
    assert diag.message_primary and f'"{eur}"' in diag.message_primary
    assert diag.sqlstate == "42P01"


def test_exception_class(conn):
    cur = conn.cursor()

    with pytest.raises(e.DatabaseError) as excinfo:
        cur.execute("select * from nonexist")

    assert isinstance(excinfo.value, e.UndefinedTable)
    assert isinstance(excinfo.value, conn.ProgrammingError)


def test_exception_class_fallback(conn):
    cur = conn.cursor()

    x = e._sqlcodes.pop("42P01")
    try:
        with pytest.raises(e.Error) as excinfo:
            cur.execute("select * from nonexist")
    finally:
        e._sqlcodes["42P01"] = x

    assert type(excinfo.value) is conn.ProgrammingError


def test_lookup():
    assert e.lookup("42P01") is e.UndefinedTable
    assert e.lookup("42p01") is e.UndefinedTable
    assert e.lookup("UNDEFINED_TABLE") is e.UndefinedTable
    assert e.lookup("undefined_table") is e.UndefinedTable

    with pytest.raises(KeyError):
        e.lookup("XXXXX")


def test_error_sqlstate():
    assert e.Error.sqlstate is None
    assert e.ProgrammingError.sqlstate is None
    assert e.UndefinedTable.sqlstate == "42P01"


def test_error_pickle(conn):
    cur = conn.cursor()
    with pytest.raises(e.DatabaseError) as excinfo:
        cur.execute("select 1 from wat")

    exc = pickle.loads(pickle.dumps(excinfo.value))
    assert isinstance(exc, e.UndefinedTable)
    assert exc.diag.sqlstate == "42P01"


def test_diag_pickle(conn):
    cur = conn.cursor()
    with pytest.raises(e.DatabaseError) as excinfo:
        cur.execute("select 1 from wat")

    diag1 = excinfo.value.diag
    diag2 = pickle.loads(pickle.dumps(diag1))

    assert isinstance(diag2, type(diag1))
    for f in pq.DiagnosticField:
        if f == pq.DiagnosticField.SEVERITY_NONLOCALIZED:
            continue
        assert getattr(diag1, f.name.lower()) == getattr(diag2, f.name.lower())

    assert diag2.sqlstate == "42P01"


@pytest.mark.slow
@pytest.mark.xfail(
    (pq.__impl__ in ("c", "binary") and sys.version_info[:2] == (3, 12)),
    reason="Something with Exceptions, C, Python 3.12",
)
def test_diag_survives_cursor(conn, gc_collect):
    cur = conn.cursor()
    with pytest.raises(e.Error) as exc:
        cur.execute("select * from nosuchtable")

    diag = exc.value.diag
    del exc
    w = ref(cur)
    del cur
    gc_collect()
    assert w() is None
    assert diag.sqlstate == "42P01"


def test_diag_independent(conn):
    conn.autocommit = True
    cur = conn.cursor()

    with pytest.raises(e.Error) as exc1:
        cur.execute("l'acqua e' poca e 'a papera nun galleggia")

    with pytest.raises(e.Error) as exc2:
        cur.execute("select level from water where ducks > 1")

    assert exc1.value.diag.sqlstate == "42601"
    assert exc2.value.diag.sqlstate == "42P01"


@pytest.mark.crdb_skip("deferrable")
def test_diag_from_commit(conn):
    cur = conn.cursor()
    cur.execute(
        """
        create temp table test_deferred (
           data int primary key,
           ref int references test_deferred (data)
               deferrable initially deferred)
    """
    )
    cur.execute("insert into test_deferred values (1,2)")
    with pytest.raises(e.Error) as exc:
        conn.commit()

    assert exc.value.diag.sqlstate == "23503"


@pytest.mark.crdb_skip("deferrable")
async def test_diag_from_commit_async(aconn):
    cur = aconn.cursor()
    await cur.execute(
        """
        create temp table test_deferred (
           data int primary key,
           ref int references test_deferred (data)
               deferrable initially deferred)
    """
    )
    await cur.execute("insert into test_deferred values (1,2)")
    with pytest.raises(e.Error) as exc:
        await aconn.commit()

    assert exc.value.diag.sqlstate == "23503"


def test_query_context(conn):
    with pytest.raises(e.Error) as exc:
        conn.execute("select * from wat")

    s = str(exc.value)
    if not is_crdb(conn):
        assert "from wat" in s, s
    assert exc.value.diag.message_primary
    assert exc.value.diag.message_primary in s
    assert "ERROR" not in s
    assert not s.endswith("\n")


@pytest.mark.crdb_skip("do")
def test_unknown_sqlstate(conn):
    code = "PXX99"
    with pytest.raises(KeyError):
        e.lookup(code)

    with pytest.raises(e.ProgrammingError) as excinfo:
        conn.execute(
            f"""
            do $$begin
            raise exception 'made up code' using errcode = '{code}';
            end$$ language plpgsql
            """
        )
    exc = excinfo.value
    assert exc.diag.sqlstate == code
    assert exc.sqlstate == code
    # Survives pickling too
    pexc = pickle.loads(pickle.dumps(exc))
    assert pexc.sqlstate == code


def test_pgconn_error(conn_cls):
    with pytest.raises(gaussdb.OperationalError) as excinfo:
        conn_cls.connect("dbname=nosuchdb")

    exc = excinfo.value
    assert exc.pgconn
    assert exc.pgconn.db == b"nosuchdb"


def test_pgconn_error_pickle(conn_cls):
    with pytest.raises(gaussdb.OperationalError) as excinfo:
        conn_cls.connect("dbname=nosuchdb")

    exc = pickle.loads(pickle.dumps(excinfo.value))
    assert exc.pgconn is None


def test_pgresult(conn):
    with pytest.raises(e.DatabaseError) as excinfo:
        conn.execute("select 1 from wat")

    exc = excinfo.value
    assert exc.pgresult
    assert exc.pgresult.error_field(pq.DiagnosticField.SQLSTATE) == b"42P01"


def test_pgresult_pickle(conn):
    with pytest.raises(e.DatabaseError) as excinfo:
        conn.execute("select 1 from wat")

    exc = pickle.loads(pickle.dumps(excinfo.value))
    assert exc.pgresult is None
    assert exc.diag.sqlstate == "42P01"


def test_blank_sqlstate(conn):
    assert e.get_base_exception("") is e.DatabaseError


@pytest.mark.parametrize(
    "msg",
    [
        'connection to server at "2001:1488:fffe:20::229", port 5432 failed',
        "HORROR: foo\n",
    ],
)
def test_strip_severity_unstripped(msg):
    from gaussdb.pq.misc import strip_severity

    out = strip_severity(msg)
    assert out == msg.strip()


@pytest.mark.parametrize(
    "msg",
    [
        "ERROR: foo\n",
        "ERRORE: foo\nbar\n",
        "오류: foo: bar",
    ],
)
def test_strip_severity_l10n(msg):
    from gaussdb.pq.misc import strip_severity

    out = strip_severity(msg)
    assert out == msg.split(":", 1)[1].strip()
