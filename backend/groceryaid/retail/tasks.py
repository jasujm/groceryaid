"""Retail tasks"""

from .. import db

from . import sok, faker
from .common import RetailChain

store_modules = {
    RetailChain.FAKER: faker,
    RetailChain.SOK: sok,
}


async def fetch_and_save_stores_and_prices(chain: RetailChain):
    """Fetch all stores and prices via external APIs"""
    module = store_modules[chain]
    for store_external_id in module.get_store_external_ids():
        async with db.get_connection() as connection, module.StoreFetcher(
            store_external_id
        ) as fetcher:
            store = fetcher.get_store()
            await db.create(db.stores, store.dict(), connection=connection)
            async for prices in fetcher.get_prices_in_batches():
                await db.create(
                    db.prices, [price.dict() for price in prices], connection=connection
                )
