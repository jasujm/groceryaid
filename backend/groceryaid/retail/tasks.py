"""Retail tasks"""

from .. import db

from . import sok

from ..settings import settings


async def fetch_and_save_stores_and_prices():
    """Fetch all stores and prices via external APIs"""
    for store_external_id in settings.sok_store_ids:
        async with db.get_connection() as connection, sok.StoreFetcher(
            store_external_id
        ) as fetcher:
            store = fetcher.get_store()
            await db.create(db.stores, store.dict(), connection=connection)
            async for prices in fetcher.get_prices_in_batches():
                await db.create(
                    db.prices, [price.dict() for price in prices], connection=connection
                )
