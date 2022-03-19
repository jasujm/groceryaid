"""Database services"""

import asyncio

import sqlalchemy
import sqlalchemy.ext.asyncio as sqlaio
import sqlalchemy_utils.types as sqlt

from .retail import RetailChain

# TODO: store URL in environment
engine = sqlaio.create_async_engine(
    "postgresql+asyncpg://groceryaid@localhost:5432/groceryaid"
)

meta = sqlalchemy.MetaData()


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
    meta,
    sqlalchemy.Column("id", sqlt.uuid.UUIDType, primary_key=True),
    sqlalchemy.Column("chain", sqlalchemy.Enum(RetailChain), nullable=False),
    sqlalchemy.Column("external_id", sqlalchemy.String(31), nullable=False),
    sqlalchemy.Column("name", sqlalchemy.String(255), nullable=False),
    *_get_timestamp_columns(),
    sqlalchemy.UniqueConstraint("chain", "external_id")
)

prices = sqlalchemy.Table(
    "prices",
    meta,
    sqlalchemy.Column(
        "store_id",
        sqlt.uuid.UUIDType,
        sqlalchemy.ForeignKey("stores.id"),
        primary_key=True,
    ),
    sqlalchemy.Column("ean", sqlalchemy.CHAR(13), primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("price", sqlalchemy.DECIMAL(7, 2), nullable=False),
    *_get_timestamp_columns(),
)


async def init():
    """Initialize database"""
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)


if __name__ == "__main__":
    asyncio.run(init())
