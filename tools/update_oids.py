#!/usr/bin/env python
"""
Update the maps of builtin types and names.

This script updates some of the files in gaussdb source code with data read
from a database catalog.

Hint: use docker to upgrade types from a new version in isolation. Run:

    docker run --rm -p 11111:5432 --name pg -e GAUSSDB_PASSWORD=password gaussdb:TAG

with a specified version tag, and then query it using:

    %(prog)s "host=localhost port=11111 user=root password=password"
"""

from __future__ import annotations

import re
import argparse
import subprocess as sp
from pathlib import Path

import gaussdb
from gaussdb.pq import version_pretty
from gaussdb.crdb import CrdbConnection
from gaussdb.rows import TupleRow
from gaussdb._compat import TypeAlias

Connection: TypeAlias = gaussdb.Connection[TupleRow]

ROOT = Path(__file__).parent.parent


def main() -> None:
    opt = parse_cmdline()
    conn = gaussdb.connect(opt.dsn, autocommit=True)

    if CrdbConnection.is_crdb(conn):
        conn = CrdbConnection.connect(opt.dsn, autocommit=True)
        update_crdb_python_oids(conn)
    else:
        update_python_oids(conn)
        update_python_types(conn)


def update_python_types(conn: Connection) -> None:
    fn = ROOT / "gaussdb/gaussdb/gaussdb.py"

    lines = []
    lines.extend(get_version_comment(conn))
    lines.extend(get_py_types(conn))
    lines.extend(get_py_ranges(conn))

    update_file(fn, lines)
    sp.check_call(["black", "-q", fn])


def update_python_oids(conn: Connection) -> None:
    fn = ROOT / "gaussdb/gaussdb/_oids.py"

    lines = []
    lines.extend(get_version_comment(conn))
    lines.extend(get_py_oids(conn))

    update_file(fn, lines)
    sp.check_call(["black", "-q", fn])


def update_crdb_python_oids(conn: Connection) -> None:
    fn = ROOT / "gaussdb/gaussdb/crdb/_types.py"

    lines = []
    lines.extend(get_version_comment(conn))
    lines.extend(get_py_types(conn))

    update_file(fn, lines)
    sp.check_call(["black", "-q", fn])


def get_version_comment(conn: Connection) -> list[str]:
    if conn.info.vendor == "PostgreSQL":
        # version = version_pretty(conn.info.server_version)
        raw_version = conn.info.server_version

        if isinstance(raw_version, str):
            # such as '505.2.0' → [505, 2, 0]
            parts = [int(x) for x in re.findall(r"\d+", raw_version)]
            if len(parts) >= 2:
                major, minor = parts[0], parts[1]
                patch = parts[2] if len(parts) >= 3 else 0
                version_int = major * 10000 + minor * 100 + patch
            else:
                version_int = 0  # fallback
        else:
            version_int = raw_version

        version = version_pretty(version_int)
    elif conn.info.vendor == "CockroachDB":
        assert isinstance(conn, CrdbConnection)
        version = version_pretty(conn.info.server_version)
    else:
        raise NotImplementedError(f"unexpected vendor: {conn.info.vendor}")
    return ["", f"    # Generated from {conn.info.vendor} {version}", ""]


def get_py_oids(conn: Connection) -> list[str]:
    lines = []
    for typname, oid in conn.execute(
        """
select typname, oid
from pg_type
where
    oid < 10000
    and (typtype = any('{b,r,m}') or typname = 'record')
    and (typname !~ '^(_|pg_)' or typname = 'pg_lsn')
order by typname
"""
    ):
        const_name = typname.upper() + "_OID"
        lines.append(f"{const_name} = {oid}")

    return lines


typemods = {
    "char": "CharTypeModifier",
    "bpchar": "CharTypeModifier",
    "varchar": "CharTypeModifier",
    "numeric": "NumericTypeModifier",
    "time": "TimeTypeModifier",
    "timetz": "TimeTypeModifier",
    "timestamp": "TimeTypeModifier",
    "timestamptz": "TimeTypeModifier",
    "interval": "TimeTypeModifier",
    "bit": "BitTypeModifier",
    "varbit": "BitTypeModifier",
}


def get_py_types(conn: Connection) -> list[str]:
    # Note: "record" is a pseudotype but still a useful one to have.
    # "pg_lsn" is a documented public type and useful in streaming replication
    lines = []
    for typname, oid, typarray, regtype, typdelim in conn.execute(
        """
select typname, oid, typarray,
    -- CRDB might have quotes in the regtype representation
    replace(CAST(typname AS TEXT), '''', '') as regtype,
    typdelim
from pg_type t
where
    oid < 10000
    and oid != '"char"'::regtype
    and (typtype = 'b' or typname = 'record')
    and (typname !~ '^(_|pg_)' or typname = 'pg_lsn')
order by typname
"""
    ):
        typemod = typemods.get(typname)

        # Weird legacy type in gaussdb catalog
        if typname == "char":
            typname = regtype = '"char"'

        # https://github.com/cockroachdb/cockroach/issues/81645
        if typname == "int4" and conn.info.vendor == "CockroachDB":
            regtype = typname

        params = [repr(typname), str(oid), str(typarray)]
        if regtype != typname:
            params.append(f"regtype={regtype!r}")
        if typemod:
            params.append(f"typemod={typemod}")
        if typdelim != ",":
            params.append(f"delimiter={typdelim!r}")
        lines.append(f"TypeInfo({','.join(params)}),")

    return lines


def get_py_ranges(conn: Connection) -> list[str]:
    lines = []
    for typname, oid, typarray, rngsubtype in conn.execute(
        """
select t.typname, t.oid, t.typarray, r.rngsubtype
from
    pg_type t
    join pg_range r on t.oid = r.rngtypid
where
    t.oid < 10000
    and t.typtype = 'r'
order by t.typname
"""
    ):
        params = [f"{typname!r}, {oid}, {typarray}, subtype_oid={rngsubtype}"]
        lines.append(f"RangeInfo({','.join(params)}),")

    return lines


def update_file(fn: Path, new: list[str]) -> None:
    with fn.open("r") as f:
        lines = f.read().splitlines()
    istart, iend = (
        i
        for i, line in enumerate(lines)
        if re.match(r"\s*#\s*autogenerated:\s+(start|end)", line)
    )
    lines[istart + 1 : iend] = new + [""]

    with fn.open("w") as f:
        f.write("\n".join(lines))
        f.write("\n")


def parse_cmdline() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("dsn", help="where to connect to")
    opt = parser.parse_args()
    return opt


if __name__ == "__main__":
    main()
