"""Database utilities

Provides wrappers for executing queries in the default database, as well as
abstraction layer over common CRUD operations.
"""

import contextlib
import typing

import sqlalchemy
import sqlalchemy.engine
import sqlalchemy.ext.asyncio as sqlaio

from . import _db


def _to_sequence(value):
    if isinstance(value, typing.Sequence) and not isinstance(value, (str, bytes)):
        return value
    return [value]


def _begin_connection(
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
) -> typing.AsyncContextManager[sqlaio.AsyncConnection]:
    if connection:
        return contextlib.nullcontext(connection)
    return _db.get_connection()


async def execute(
    *args,
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
    **kwargs,
):
    """Execute a SQL expression in the default database

    Keyword Arguments:
       connection: Database connection, or `None` to use a fresh connection
    """
    async with _begin_connection(connection) as conn:
        return await conn.execute(*args, **kwargs)


async def create(
    table: sqlalchemy.Table,
    objs: typing.Any,
    *,
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
):
    """Insert `objs` into `table` in the default database

    Parameters:
        table: Database table
        objs: Object/objects to insert

    Keyword Arguments:
        connection: Database connection, or `None` to use a fresh connection
    """
    return await execute(table.insert(), objs, connection=connection)


async def read(
    table: sqlalchemy.Table,
    pk: typing.Any | typing.Sequence[typing.Any],
    *,
    columns: typing.Optional[typing.Sequence[sqlalchemy.Column]] = None,
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
) -> sqlalchemy.engine.CursorResult:  # type: ignore
    """Read a row(s) from ``table`` by primary key

    Parameters:
       table: The database table
       pk: Primary key value

    Keyword Arguments:
       columns: The list of columns to select (defaults to whole table)
       connection: Database connection, or `None` to use a fresh connection

    Returns:
       The resulting row
    """
    if columns:
        select_expr = sqlalchemy.select(columns)
    else:
        select_expr = table.select()
    pk_parts = _to_sequence(pk)
    result = await execute(
        select_expr.where(*(c == p for (c, p) in zip(table.primary_key, pk_parts))),
        connection=connection,
    )
    return result.first()


async def select(
    table: sqlalchemy.Table,
    *,
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
) -> sqlalchemy.engine.CursorResult:  # type: ignore
    """Select rows from ``table``

    Parameters:
       table: The database table

    Keyword Arguments:
       connection: Database connection, or `None` to use a fresh connection

    Returns:
       The resulting rows
    """
    return await execute(table.select(), connection=connection)


async def delete(
    table: sqlalchemy.Table,
    pk: typing.Any | typing.Sequence[typing.Any],
    *,
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
):
    """Delete row(s) from ``table`` by primary key

    Parameters:
       table: The database table
       pk: Primary key value

    Keyword Arguments:
       columns: The list of columns to select (defaults to whole table)
       connection: Database connection, or `None` to use a fresh connection
    """
    pk_parts = _to_sequence(pk)
    await execute(
        table.delete().where(*(c == p for (c, p) in zip(table.primary_key, pk_parts))),
        connection=connection,
    )
