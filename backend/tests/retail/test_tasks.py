import contextlib
import itertools
import unittest.mock

import pytest

import groceryaid.db as db
from groceryaid.retail import Store, Price, RetailChain
import groceryaid.retail.faker as retail_faker
from groceryaid.retail.tasks import fetch_and_save_stores_and_prices


@pytest.mark.asyncio
async def test_fetch_store_and_prices(monkeypatch):
    store_external_ids = retail_faker.get_store_external_ids()
    fetchers = {eid: retail_faker.StoreFetcher(eid) for eid in store_external_ids}

    get_store_fetcher = unittest.mock.Mock(side_effect=lambda eid: fetchers[eid])

    monkeypatch.setattr(retail_faker, "StoreFetcher", get_store_fetcher)

    await fetch_and_save_stores_and_prices(RetailChain.FAKER)

    stores_in_db = await db.read(db.stores)
    assert [Store(**row) for row in stores_in_db] == [
        fetcher.store for fetcher in fetchers.values()
    ]

    prices_in_db = await db.read(db.prices)
    assert [Price(**row) for row in prices_in_db] == list(
        itertools.chain.from_iterable(fetcher.prices for fetcher in fetchers.values())
    )
