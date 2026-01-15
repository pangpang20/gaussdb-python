"""
Objects to return information about a GaussDB connection.
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

from pathlib import Path
from datetime import tzinfo

from . import pq
from ._tz import get_tzinfo


class ConnectionInfo:
    """Allow access to information about the connection."""

    __module__ = "gaussdb"

    def __init__(self, pgconn: pq.abc.PGconn):
        self.pgconn = pgconn

    @property
    def vendor(self) -> str:
        """A string representing the database vendor connected to."""
        return "PostgreSQL"

    @property
    def host(self) -> str:
        """The server host name of the active connection. See :pq:`PQhost()`."""
        return self._get_pgconn_attr("host")

    @property
    def hostaddr(self) -> str:
        """The server IP address of the connection. See :pq:`PQhostaddr()`."""
        return self._get_pgconn_attr("hostaddr")

    @property
    def port(self) -> int:
        """The port of the active connection. See :pq:`PQport()`."""
        return int(self._get_pgconn_attr("port"))

    @property
    def dbname(self) -> str:
        """The database name of the connection. See :pq:`PQdb()`."""
        return self._get_pgconn_attr("db")

    @property
    def user(self) -> str:
        """The user name of the connection. See :pq:`PQuser()`."""
        return self._get_pgconn_attr("user")

    @property
    def password(self) -> str:
        """The password of the connection. See :pq:`PQpass()`."""
        return self._get_pgconn_attr("password")

    @property
    def options(self) -> str:
        """
        The command-line options passed in the connection request.
        See :pq:`PQoptions`.
        """
        return self._get_pgconn_attr("options")

    def get_parameters(self) -> dict[str, str]:
        """Return the connection parameters values.

        Return all the parameters set to a non-default value, which might come
        either from the connection string and parameters passed to
        `~Connection.connect()` or from environment variables. The password
        is never returned (you can read it using the `password` attribute).

        Note:
            GaussDB does not support PGconn.info attribute, uses fallback method.
        """
        pyenc = self.encoding

        # Check if info attribute is supported (GaussDB does not support)
        try:
            info = self.pgconn.info
            if info is None:
                return self._get_parameters_fallback()
        except (AttributeError, NotImplementedError):
            return self._get_parameters_fallback()

        # PostgreSQL normal path
        try:
            # Get the known defaults to avoid reporting them
            defaults = {
                i.keyword: i.compiled
                for i in pq.Conninfo.get_defaults()
                if i.compiled is not None
            }
            # Not returned by the libq. Bug? Bet we're using SSH.
            defaults.setdefault(b"channel_binding", b"prefer")
            defaults[b"passfile"] = str(Path.home() / ".pgpass").encode()

            return {
                i.keyword.decode(pyenc): i.val.decode(pyenc)
                for i in info
                if i.val is not None
                and i.keyword != b"password"
                and i.val != defaults.get(i.keyword)
            }
        except Exception:
            # Use fallback on error
            return self._get_parameters_fallback()

    def _get_parameters_fallback(self) -> dict[str, str]:
        """Fallback method for getting connection parameters.

        When PGconn.info is not available (e.g., GaussDB),
        retrieve basic connection information from other sources.
        """
        params = {}

        # Get available information from pgconn attributes
        if self.pgconn.host:
            params["host"] = self.pgconn.host.decode(self.encoding, errors="replace")

        if self.pgconn.port:
            params["port"] = self.pgconn.port.decode(self.encoding, errors="replace")

        if self.pgconn.db:
            params["dbname"] = self.pgconn.db.decode(self.encoding, errors="replace")

        if self.pgconn.user:
            params["user"] = self.pgconn.user.decode(self.encoding, errors="replace")

        # Get other available parameters
        try:
            if hasattr(self.pgconn, "options") and self.pgconn.options:
                params["options"] = self.pgconn.options.decode(
                    self.encoding, errors="replace"
                )
        except Exception:
            pass

        return params

    @property
    def dsn(self) -> str:
        """Return the connection string to connect to the database.

        The string contains all the parameters set to a non-default value,
        which might come either from the connection string and parameters
        passed to `~Connection.connect()` or from environment variables. The
        password is never returned (you can read it using the `password`
        attribute).
        """
        try:
            params = self.get_parameters()
        except Exception:
            params = self._get_parameters_fallback()

        if not params:
            return ""

        # Build DSN string
        parts = []
        for key, value in params.items():
            if key == "password":
                continue  # Do not include password
            # Escape values
            if " " in value or "=" in value or "'" in value:
                value = "'" + value.replace("'", "\\'") + "'"
            parts.append(f"{key}={value}")

        return " ".join(parts)

    @property
    def status(self) -> pq.ConnStatus:
        """The status of the connection. See :pq:`PQstatus()`."""
        return pq.ConnStatus(self.pgconn.status)

    @property
    def transaction_status(self) -> pq.TransactionStatus:
        """
        The current in-transaction status of the session.
        See :pq:`PQtransactionStatus()`.
        """
        return pq.TransactionStatus(self.pgconn.transaction_status)

    @property
    def pipeline_status(self) -> pq.PipelineStatus:
        """
        The current pipeline status of the client.
        See :pq:`PQpipelineStatus()`.
        """
        return pq.PipelineStatus(self.pgconn.pipeline_status)

    def parameter_status(self, param_name: str) -> str | None:
        """
        Return a parameter setting of the connection.

        Return `None` is the parameter is unknown.
        """
        res = self.pgconn.parameter_status(param_name.encode(self.encoding))
        return res.decode(self.encoding) if res is not None else None

    @property
    def server_version(self) -> int:
        """
        An integer representing the server version. See :pq:`PQserverVersion()`.
        """
        return self.pgconn.server_version

    @property
    def backend_pid(self) -> int:
        """
        The process ID (PID) of the backend process handling this connection.
        See :pq:`PQbackendPID()`.
        """
        return self.pgconn.backend_pid

    @property
    def error_message(self) -> str:
        """
        The error message most recently generated by an operation on the connection.
        See :pq:`PQerrorMessage()`.
        """
        return self._get_pgconn_attr("error_message")

    @property
    def timezone(self) -> tzinfo:
        """The Python timezone info of the connection's timezone."""
        return get_tzinfo(self.pgconn)

    @property
    def encoding(self) -> str:
        """The Python codec name of the connection's client encoding."""
        return self.pgconn._encoding

    def _get_pgconn_attr(self, name: str) -> str:
        value: bytes = getattr(self.pgconn, name)
        return value.decode(self.encoding)
