"""
Wrappers for numeric types.
"""

# Copyright (C) 2020 The Psycopg Team

# Wrappers to force numbers to be cast as specific GaussDB types

# These types are implemented here but exposed by `gaussdb.types.numeric`.
# They are defined here to avoid a circular import.
_MODULE = "gaussdb.types.numeric"


class Int2(int):
    """
    Force dumping a Python `!int` as a GaussDB :sql:`smallint/int2`.
    """

    __module__ = _MODULE
    __slots__ = ()

    def __new__(cls, arg: int) -> "Int2":
        return super().__new__(cls, arg)

    def __str__(self) -> str:
        return super().__repr__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"


class Int4(int):
    """
    Force dumping a Python `!int` as a GaussDB :sql:`integer/int4`.
    """

    __module__ = _MODULE
    __slots__ = ()

    def __new__(cls, arg: int) -> "Int4":
        return super().__new__(cls, arg)

    def __str__(self) -> str:
        return super().__repr__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"


class Int8(int):
    """
    Force dumping a Python `!int` as a GaussDB :sql:`bigint/int8`.
    """

    __module__ = _MODULE
    __slots__ = ()

    def __new__(cls, arg: int) -> "Int8":
        return super().__new__(cls, arg)

    def __str__(self) -> str:
        return super().__repr__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"


class IntNumeric(int):
    """
    Force dumping a Python `!int` as a GaussDB :sql:`numeric/decimal`.
    """

    __module__ = _MODULE
    __slots__ = ()

    def __new__(cls, arg: int) -> "IntNumeric":
        return super().__new__(cls, arg)

    def __str__(self) -> str:
        return super().__repr__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"


class Float4(float):
    """
    Force dumping a Python `!float` as a GaussDB :sql:`float4/real`.
    """

    __module__ = _MODULE
    __slots__ = ()

    def __new__(cls, arg: float) -> "Float4":
        return super().__new__(cls, arg)

    def __str__(self) -> str:
        return super().__repr__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"


class Float8(float):
    """
    Force dumping a Python `!float` as a GaussDB :sql:`float8/double precision`.
    """

    __module__ = _MODULE
    __slots__ = ()

    def __new__(cls, arg: float) -> "Float8":
        return super().__new__(cls, arg)

    def __str__(self) -> str:
        return super().__repr__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"


class Oid(int):
    """
    Force dumping a Python `!int` as a GaussDB :sql:`oid`.
    """

    __module__ = _MODULE
    __slots__ = ()

    def __new__(cls, arg: int) -> "Oid":
        return super().__new__(cls, arg)

    def __str__(self) -> str:
        return super().__repr__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"
