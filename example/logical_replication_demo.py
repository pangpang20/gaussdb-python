# -*- coding: utf-8 -*-

import os
import sys

from gaussdb import connect

# Set the GaussDB implementation
os.environ["GAUSSDB_IMPL"] = "python"

# Constants
SLOT_NAME = "demo_slot"
SCHEMA = "demo_schema"
TABLE = "demo_table"


def _slot_exists(conn, slot_name):
    """Check if a replication slot exists."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(1) FROM pg_replication_slots WHERE slot_name = %s",
            (slot_name,),
        )
        row = cur.fetchone()
        return bool(row and row[0] > 0)


def _cleanup_slot_and_schema(conn):
    """Clean up replication slot and schema."""
    with conn.cursor() as cur:
        # Drop replication slot if it exists
        try:
            cur.execute(
                "SELECT count(1) FROM pg_replication_slots WHERE slot_name = %s",
                (SLOT_NAME,),
            )
            if cur.fetchone()[0] > 0:
                cur.execute("SELECT pg_drop_replication_slot(%s);", (SLOT_NAME,))
        except Exception as e:
            print(f"Error dropping slot: {e}")

        # Drop schema if it exists
        try:
            cur.execute(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE;")
        except Exception as e:
            print(f"Error dropping schema: {e}")
        conn.commit()


def _create_slot(conn):
    """Create a logical replication slot."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM pg_create_logical_replication_slot(%s, %s);",
            (SLOT_NAME, "mppdb_decoding"),
        )
        conn.commit()
        print(f"Created replication slot: {SLOT_NAME}")


def _read_changes(conn):
    """Read changes from the replication slot."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT data FROM pg_logical_slot_get_changes(%s, NULL, %s);",
            (SLOT_NAME, 4096),
        )
        rows = cur.fetchall()
        return [str(row[0]) for row in rows if row and row[0] is not None]


def main():
    # Get database connection string from environment variable
    dsn = os.environ.get("GAUSSDB_TEST_DSN")
    if not dsn:
        print("Please set the GAUSSDB_TEST_DSN environment variable, for example:")
        print(
            '   export GAUSSDB_TEST_DSN="dbname=test01 user=root password=*** '
            'host=** port=8000"'
        )
        sys.exit(1)

    # Connect to the database
    with connect(
        dsn, connect_timeout=10, application_name="logical-replication-demo"
    ) as conn:
        # Display server information
        with conn.cursor() as cur:
            server_version = conn.execute("SELECT version()").fetchall()[0][0]
            print(f"Connected. Server version: {server_version}")
            print(f"Vendor: {conn.info.vendor}, Version: {conn.info.server_version}")

        # Clean up any existing slot and schema
        _cleanup_slot_and_schema(conn)

        # Set up schema and table
        with conn.cursor() as cur:
            cur.execute(f"CREATE SCHEMA {SCHEMA};")
            cur.execute(f"SET search_path TO {SCHEMA};")
            cur.execute(
                f"CREATE TABLE {TABLE} (id int PRIMARY KEY, name varchar(255));"
            )
            cur.execute(f"ALTER TABLE {TABLE} REPLICA IDENTITY FULL;")
            conn.commit()
            print(f"Created schema {SCHEMA} and table {TABLE}")

        # Create replication slot
        _create_slot(conn)

        # Perform CRUD operations
        with conn.cursor() as cur:
            # Insert
            cur.execute(f"INSERT INTO {TABLE} VALUES (%s, %s);", (1, "hello world"))
            conn.commit()
            print("Inserted: (1, 'hello world')")

            # Update
            cur.execute(
                f"UPDATE {TABLE} SET name = %s WHERE id = %s;", ("hello gaussdb", 1)
            )
            conn.commit()
            print("Updated: name to 'hello gaussdb' for id=1")

            # Delete
            cur.execute(f"DELETE FROM {TABLE} WHERE id = %s;", (1,))
            conn.commit()
            print("Deleted: row with id=1")

        # Read and display replication changes
        changes = _read_changes(conn)
        print("\nReplication changes:")
        for change in changes:
            print(change)

        # Clean up
        _cleanup_slot_and_schema(conn)
        print(f"Cleaned up slot {SLOT_NAME} and schema {SCHEMA}")


if __name__ == "__main__":
    main()
