# -*- coding: utf-8 -*-

import os
import sys

from gaussdb import connect

os.environ["GAUSSDB_IMPL"] = "python"


def main():
    dsn = os.environ.get("GAUSSDB_TEST_DSN")
    if not dsn:
        print("❌ Please set the GAUSSDB_TEST_DSN environment variable, for example:")
        print(
            '   export GAUSSDB_TEST_DSN="dbname=test01 user=root password=***'
            'host=** port=8000"'
        )
        sys.exit(1)

    drop_table_sql = "DROP TABLE IF EXISTS test"
    create_table_sql = (
        "CREATE TABLE test (id serial PRIMARY KEY, num integer, data text)"
    )
    insert_data_sql = "INSERT INTO test (num, data) VALUES (%s, %s)"
    update_data_sql = "UPDATE test SET data = 'gaussdb' WHERE num = 2"
    select_sql = "SELECT * FROM test"

    with connect(dsn, connect_timeout=10, application_name="gaussdb-demo") as conn:

        with conn.cursor() as cur:
            server_version = conn.execute("select version()").fetchall()[0][0]
            print(f"✅ Connected. Server version: {server_version}")
            print(f"Vendor: {conn.info.vendor}, Version: {conn.info.server_version}")

            cur.execute(drop_table_sql)
            cur.execute(create_table_sql)
            cur.execute(insert_data_sql, (1, "hello"))
            cur.execute(insert_data_sql, (2, "world"))

            cur.execute(select_sql)
            print("📄origin: ", cur.fetchall())

            cur.execute(update_data_sql)
            cur.execute(select_sql)
            print("📄update: ", cur.fetchall())


if __name__ == "__main__":
    main()
