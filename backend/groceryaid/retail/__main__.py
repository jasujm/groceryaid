"""Fetch and save retail info"""

import asyncio

from .. import db

from . import sok


async def fetch_and_save_stores_and_prices():
    """Fetch all stores and prices via external APIs"""
    store, prices = await sok.fetch_store_and_prices()
    async with db.engine.begin() as connection:
        await connection.execute(db.stores.insert(), store)
        await connection.execute(db.prices.insert(), prices)


if __name__ == "__main__":
    asyncio.run(fetch_and_save_stores_and_prices())
