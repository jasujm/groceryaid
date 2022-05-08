"""Database setup

This module contains the basic SQLAlchemy definitions needed to setup the
database environment.
"""

import typing

import sqlalchemy
import sqlalchemy.ext.asyncio as sqlaio
import sqlalchemy_utils.types as sqlt

from ..retail import RetailChain
from ..settings import settings

_engine = sqlaio.create_async_engine(settings.database_url)

_meta = sqlalchemy.MetaData()


def _get_timestamp_columns():
    return [
        sqlalchemy.Column(
            "created_at",
            sqlalchemy.DateTime(timezone=True),
            nullable=False,
            default=sqlalchemy.func.now(),
        ),
        sqlalchemy.Column(
            "updated_at",
            sqlalchemy.DateTime(timezone=True),
            nullable=False,
            default=sqlalchemy.func.now(),
            onupdate=sqlalchemy.func.now(),
        ),
    ]


stores = sqlalchemy.Table(
    "stores",
    _meta,
    sqlalchemy.Column("id", sqlt.uuid.UUIDType, primary_key=True),
    sqlalchemy.Column("chain", sqlalchemy.Enum(RetailChain), nullable=False),
    sqlalchemy.Column("external_id", sqlalchemy.String(36), nullable=False),
    sqlalchemy.Column("name", sqlalchemy.String(255), nullable=False),
    *_get_timestamp_columns(),
    sqlalchemy.UniqueConstraint("chain", "external_id"),
)

products = sqlalchemy.Table(
    "products",
    _meta,
    sqlalchemy.Column("id", sqlt.uuid.UUIDType, primary_key=True),
    sqlalchemy.Column(
        "store_id",
        sqlalchemy.ForeignKey("stores.id"),
        nullable=False,
    ),
    sqlalchemy.Column("ean", sqlalchemy.CHAR(13), nullable=False),
    sqlalchemy.Column("name", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("price", sqlalchemy.DECIMAL(7, 2), nullable=False),
    *_get_timestamp_columns(),
    sqlalchemy.UniqueConstraint("store_id", "ean"),
)


storevisits = sqlalchemy.Table(
    "storevisits",
    _meta,
    sqlalchemy.Column("id", sqlt.uuid.UUIDType, primary_key=True),
    sqlalchemy.Column(
        "store_id",
        sqlalchemy.ForeignKey("stores.id"),
    ),
    *_get_timestamp_columns(),
)


cartproducts = sqlalchemy.Table(
    "cartproducts",
    _meta,
    sqlalchemy.Column(
        "storevisit_id", sqlalchemy.ForeignKey("storevisits.id"), primary_key=True
    ),
    sqlalchemy.Column("rank", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column(
        "product_id", sqlalchemy.ForeignKey("products.id"), nullable=False
    ),
    sqlalchemy.Column("quantity", sqlalchemy.Integer, nullable=False),
    *_get_timestamp_columns(),
)


def get_metadata() -> sqlalchemy.MetaData:
    """Return the database metadata"""
    return _meta


def get_engine() -> sqlaio.AsyncEngine:
    """Return the default database engine"""
    return _engine


def get_connection() -> typing.AsyncContextManager[sqlaio.AsyncConnection]:
    """Return database connection"""
    return get_engine().begin()


async def init():
    """Initialize database"""
    async with get_engine().begin() as conn:
        await conn.run_sync(_meta.create_all)
