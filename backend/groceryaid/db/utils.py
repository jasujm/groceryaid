"""Database utilities

Provides wrappers for executing queries in the default database, as well as
abstraction layer over common CRUD operations.
"""

import contextlib
import functools
import operator
import typing

import sqlalchemy
from sqlalchemy.dialects import postgresql
import sqlalchemy.engine
import sqlalchemy.ext.asyncio as sqlaio
from sqlalchemy.sql.expression import ColumnElement

from . import _db


def _to_sequence(value):
    if isinstance(value, typing.Sequence) and not isinstance(value, (str, bytes)):
        return value
    return [value]


def _pk_sequence_to_where_expr(
    table: sqlalchemy.Table, pk: typing.Sequence[typing.Any]
):
    return functools.reduce(
        operator.and_, (c == p for (c, p) in zip(table.primary_key, pk))
    )


def _pk_to_where_expr(
    table: sqlalchemy.Table,
    pk: typing.Any | typing.Sequence[typing.Any] | ColumnElement,
):
    if isinstance(pk, ColumnElement):
        return pk
    return _pk_sequence_to_where_expr(table, _to_sequence(pk))


def _columns_to_select_expr(
    table: sqlalchemy.Table,
    columns: typing.Optional[typing.Sequence[sqlalchemy.Column]],
):
    if columns:
        return sqlalchemy.select(columns)
    return table.select()


def begin_connection(
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
) -> typing.AsyncContextManager[sqlaio.AsyncConnection]:
    """Begin transaction, or continue an existing one

    Arguments:
        connection: Database connection, or ``None`` to use a fresh connection

    Returns:
        ``connection`` wrapped in null context manager if it exists, otherwise a new
        connection
    """
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
       connection: Database connection, or ``None`` to use a fresh connection
    """
    async with begin_connection(connection) as conn:
        return await conn.execute(*args, **kwargs)


async def create(
    table: sqlalchemy.Table,
    objs: typing.Mapping | typing.Sequence[typing.Mapping],
    *,
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
):
    """Insert ``objs`` into ``table`` in the default database

    Parameters:
        table: Database table
        objs: Object/objects to insert

    Keyword Arguments:
        connection: Database connection, or ``None`` to use a fresh connection
    """
    return await execute(table.insert(), objs, connection=connection)


async def upsert(
    table: sqlalchemy.Table,
    objs: typing.Mapping | typing.Sequence[typing.Mapping],
    *,
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
):
    """Upsert ``objs`` into ``table``

    Parameters:
        table: Database table
        objs: Object/objects to insert

    Keyword Arguments:
        connection: Database connection, or ``None`` to use a fresh connection
    """
    obj = objs if isinstance(objs, typing.Mapping) else objs[0]
    pk_names = {key.name for key in table.primary_key}
    insert_stmt = postgresql.insert(table)
    set_ = {key: insert_stmt.excluded[key] for key in obj.keys() if key not in pk_names}
    set_["updated_at"] = insert_stmt.excluded.updated_at
    do_update_stmt = insert_stmt.on_conflict_do_update(
        index_elements=pk_names, set_=set_
    )
    await execute(do_update_stmt, objs, connection=connection)


async def update(
    table: sqlalchemy.Table,
    obj: typing.Mapping,
    *,
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
):
    """Update ``obj`` in ``table`` identified by primary key

    Parameters:
        table: Database table
        objs: Object/objects to insert

    Keyword Arguments:
        connection: Database connection, or ``None`` to use a fresh connection
    """
    pk_names = {key.name for key in table.primary_key}
    pk = [value for (key, value) in obj.items() if key in pk_names]
    values = {key: value for (key, value) in obj.items() if key not in pk_names}
    await execute(
        table.update().where(_pk_sequence_to_where_expr(table, pk)).values(**values),
        connection=connection,
    )


async def read(
    table: sqlalchemy.Table,
    pk: typing.Any | typing.Sequence[typing.Any] | ColumnElement,
    *,
    columns: typing.Optional[typing.Sequence[sqlalchemy.Column]] = None,
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
) -> sqlalchemy.engine.CursorResult:  # type: ignore
    """Read a row(s) from ``table`` by primary key

    Parameters:
       table: The database table
       pk: Primary key value, or a where clause

    Keyword Arguments:
       columns: The list of columns to select (defaults to whole table)
       connection: Database connection, or ``None`` to use a fresh connection

    Returns:
       The resulting row
    """
    result = await execute(
        _columns_to_select_expr(table, columns).where(_pk_to_where_expr(table, pk)),
        connection=connection,
    )
    return result.first()


async def select(
    table: sqlalchemy.Table,
    *,
    columns: typing.Optional[typing.Sequence[sqlalchemy.Column]] = None,
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
) -> sqlalchemy.engine.CursorResult:  # type: ignore
    """Select rows from ``table``

    Parameters:
       table: The database table

    Keyword Arguments:
       columns: The list of columns to select (defaults to whole table)
       connection: Database connection, or `None` to use a fresh connection

    Returns:
       The resulting rows
    """
    result = await execute(
        _columns_to_select_expr(table, columns), connection=connection
    )
    return result.fetchall()


async def delete(
    table: sqlalchemy.Table,
    pk: typing.Any | typing.Sequence[typing.Any] | ColumnElement,
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
    await execute(
        table.delete().where(_pk_to_where_expr(table, pk)),
        connection=connection,
    )
