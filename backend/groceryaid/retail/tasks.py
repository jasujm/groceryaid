"""Retail tasks"""

from .. import db

from . import sok


async def fetch_and_save_stores_and_prices():
    """Fetch all stores and prices via external APIs"""
    store, prices = await sok.fetch_store_and_prices()
    async with db.engine.begin() as connection:
        await connection.execute(db.stores.insert(), store.dict())
        await connection.execute(db.prices.insert(), [price.dict() for price in prices])
