"""Retail tasks"""

from .. import db

from . import sok


async def fetch_and_save_stores_and_prices():
    """Fetch all stores and prices via external APIs"""
    store, prices = await sok.fetch_store_and_prices()
    async with db.get_connection() as connection:
        await db.create(db.stores, store.dict(), connection=connection)
        await db.create(
            db.prices, [price.dict() for price in prices], connection=connection
        )
