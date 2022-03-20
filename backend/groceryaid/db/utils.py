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

    Parameters:
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
        connection: Database connection, or `None` to use a fresh connection
    """
    return await execute(table.insert(), objs, connection=connection)


async def read(
    table: sqlalchemy.Table,
    *,
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
) -> sqlalchemy.engine.CursorResult:  # type: ignore
    """Select rows from ``table``

    Parameters:
       table: The database table
       connection: Database connection, or `None` to use a fresh connection

    Returns:
       The result object
    """
    return await execute(table.select(), connection=connection)
