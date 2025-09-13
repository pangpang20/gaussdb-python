# -*- coding: utf-8 -*-

import os
import sys

from gaussdb import connect

os.environ["GAUSSDB_IMPL"] = "python"


def main(ssl_mode="require"):
    base_dsn = os.environ.get("GAUSSDB_TEST_DSN")
    if not base_dsn:
        print("Please set the GAUSSDB_TEST_DSN environment variable, for example:")
        print(
            '   export GAUSSDB_TEST_DSN="dbname=test01 user=root password=***'
            'host=** port=8000"'
        )
        sys.exit(1)
    ssl_root_cert = os.environ.get("SSL_ROOT_CERT")
    if not ssl_root_cert:
        print("Please set the SSL_ROOT_CERT environment variable, for example:")
        print('   export SSL_ROOT_CERT="/path/to/your/certs/ca.crt')
        sys.exit(1)

    drop_table_sql = "DROP TABLE IF EXISTS test01"
    create_table_sql = "CREATE TABLE test01 (id int, name varchar(255))"
    insert_data_sql = "INSERT INTO test01 (id, name) VALUES (%s, %s)"
    update_data_sql = "update test01 set name='hello gaussdb' where id = 1"
    select_sql = "SELECT * FROM test01"

    if ssl_mode == "require":
        dsn_gauss = f"{base_dsn} sslmode=require"
    elif ssl_mode == "verify-ca":
        dsn_gauss = f"{base_dsn} sslmode=verify-ca sslrootcert={ssl_root_cert}"
    else:
        raise ValueError("不支持的 SSL 模式，请使用 'require' 或 'verify-ca'")

    with connect(dsn_gauss, connect_timeout=10, application_name="test01") as conn:
        with conn.cursor() as cur:
            server_version = conn.execute("select version()").fetchall()[0][0]
            print(f"Server version: {server_version}")
            print(f"conn.info.vendor: {conn.info.vendor}")
            print(f"conn.info.server_version: {conn.info.server_version}")

            cur.execute(drop_table_sql)
            cur.execute(create_table_sql)
            cur.execute(insert_data_sql, (100, "abc'def"))
            cur.execute(insert_data_sql, (200, "test01"))

            cur.execute(select_sql)
            print("origin: ", cur.fetchall())

            cur.execute(update_data_sql)
            cur.execute(select_sql)
            print("update: ", cur.fetchall())


if __name__ == "__main__":
    print("require:")
    main(ssl_mode="require")
    print("verify-ca:")
    main(ssl_mode="verify-ca")
