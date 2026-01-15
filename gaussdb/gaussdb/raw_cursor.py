"""
gaussdb raw queries cursors
"""

# Copyright (C) 2023 The Psycopg Team

from __future__ import annotations

from typing import TYPE_CHECKING

from . import errors as e
from .abc import ConnectionType, Params, Query
from .sql import Composable
from .rows import Row
from ._enums import PyFormat
from .cursor import Cursor
from ._queries import GaussDBQuery
from ._cursor_base import BaseCursor
from .cursor_async import AsyncCursor
from .server_cursor import AsyncServerCursor, ServerCursor

if TYPE_CHECKING:
    from typing import Any  # noqa: F401

    from .connection import Connection  # noqa: F401
    from .connection_async import AsyncConnection  # noqa: F401


class GaussDBRawQuery(GaussDBQuery):
    """
    GaussDB raw query class.

    Only supports positional placeholders ($1, $2, ...), not named placeholders.
    """

    # Query cache size
    _CACHE_SIZE = 128

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._query_cache: dict[bytes, bytes] = {}

    def convert(self, query: Query, vars: Params | None) -> None:
        if isinstance(query, str):
            bquery = query.encode(self._encoding)
        elif isinstance(query, Composable):
            bquery = query.as_bytes(self._tx)
        else:
            bquery = query

        # Try to get from cache
        if bquery in self._query_cache:
            self.query = self._query_cache[bquery]
        else:
            # Validate query doesn't contain named placeholders
            if b"%(" in bquery:
                raise e.ProgrammingError(
                    "RawCursor does not support named placeholders (%(name)s). "
                    "Use positional placeholders ($1, $2, ...) instead."
                )

            self.query = bquery

            # Cache result
            if len(self._query_cache) < self._CACHE_SIZE:
                self._query_cache[bquery] = bquery

        self._want_formats = self._order = None
        self.dump(vars)

    def dump(self, vars: Params | None) -> None:
        """
        Serialize parameters.

        Args:
            vars: Parameter sequence (must be sequence, not dict)

        Raises:
            TypeError: If parameters are not a sequence
        """
        if vars is not None:
            if not GaussDBQuery.is_params_sequence(vars):
                raise TypeError(
                    "RawCursor requires a sequence of parameters (tuple or list), "
                    f"got {type(vars).__name__}. "
                    "For named parameters, use regular Cursor instead."
                )
            self._want_formats = [PyFormat.AUTO] * len(vars)

            self.params = self._tx.dump_sequence(vars, self._want_formats)
            self.types = self._tx.types or ()
            self.formats = self._tx.formats
        else:
            self.params = None
            self.types = ()
            self.formats = None

    def clear_cache(self) -> None:
        """Clear query cache."""
        self._query_cache.clear()


class RawCursorMixin(BaseCursor[ConnectionType, Row]):
    _query_cls = GaussDBRawQuery


class RawCursor(RawCursorMixin["Connection[Any]", Row], Cursor[Row]):
    __module__ = "gaussdb"


class AsyncRawCursor(RawCursorMixin["AsyncConnection[Any]", Row], AsyncCursor[Row]):
    __module__ = "gaussdb"


class RawServerCursor(RawCursorMixin["Connection[Any]", Row], ServerCursor[Row]):
    __module__ = "gaussdb"


class AsyncRawServerCursor(
    RawCursorMixin["AsyncConnection[Any]", Row], AsyncServerCursor[Row]
):
    __module__ = "gaussdb"
