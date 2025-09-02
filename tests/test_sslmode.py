import os

import pytest

from gaussdb import connect

SCHEMA = "test_schema"
TABLE = "test01"


@pytest.fixture(params=["require", "verify-ca"])
def dsn(request):
    """Retrieve DSN from environment variable based on SSL mode."""
    dsn = os.environ.get("GAUSSDB_TEST_DSN")
    if not dsn:
        raise ValueError("GAUSSDB_TEST_DSN environment variable not set")

    if f"sslmode={request.param}" not in dsn:
        pytest.skip(f"DSN does not match sslmode={request.param}")
    return dsn


@pytest.fixture
def db_conn(dsn):
    """Set up database connection."""
    conn = connect(dsn, connect_timeout=10, application_name="test01")
    yield conn
    conn.close()


@pytest.fixture
def setup_env(db_conn):
    """Ensure clean environment for each test."""
    cur = db_conn.cursor()
    try:
        cur.execute(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE;")
    except Exception:
        pass
    db_conn.commit()

    cur.execute(f"CREATE SCHEMA {SCHEMA};")
    cur.execute(f"SET search_path TO {SCHEMA};")
    cur.execute(f"CREATE TABLE {TABLE} (id int, name varchar(255));")
    db_conn.commit()
    yield db_conn
    try:
        cur.execute(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE;")
    except Exception:
        pass
    db_conn.commit()


def test_connection_info(setup_env):
    """Test database connection and server information."""
    cur = setup_env.cursor()
    server_version = cur.execute("SELECT version()").fetchall()[0][0]
    assert server_version is not None, "Server version should be available"
    assert setup_env.info.vendor is not None, "Vendor should be available"
    assert (
        setup_env.info.server_version is not None
    ), "Server version info should be available"


def test_table_operations(setup_env):
    """Test table creation, insertion, update, and selection."""
    cur = setup_env.cursor()
    insert_data_sql = f"INSERT INTO {SCHEMA}.{TABLE} (id, name) VALUES (%s, %s)"
    update_data_sql = f"UPDATE {SCHEMA}.{TABLE} SET name='hello gaussdb' WHERE id = 1"
    select_sql = f"SELECT * FROM {SCHEMA}.{TABLE}"

    cur.execute(insert_data_sql, (100, "abc'def"))
    cur.execute(insert_data_sql, (200, "test01"))
    setup_env.commit()

    cur.execute(select_sql)
    results = cur.fetchall()
    assert len(results) == 2, "Should have 2 rows"
    assert (100, "abc'def") in results, "First inserted row missing"
    assert (200, "test01") in results, "Second inserted row missing"

    cur.execute(update_data_sql)
    setup_env.commit()
    cur.execute(select_sql)
    updated_results = cur.fetchall()
    assert len(updated_results) == 2, "Should still have 2 rows after update"
    assert (1, "hello gaussdb") not in updated_results, "Update should not affect id=1"
    assert (100, "abc'def") in updated_results, "First row should remain unchanged"
    assert (200, "test01") in updated_results, "Second row should remain unchanged"
