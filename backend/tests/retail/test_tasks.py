import contextlib
import itertools
import unittest.mock

import pytest

import groceryaid.db as db
from groceryaid.retail import Store, Product, RetailChain
import groceryaid.retail.faker as retail_faker
from groceryaid.retail.tasks import fetch_and_save_stores_and_products


@pytest.mark.asyncio
async def test_fetch_store_and_products(monkeypatch):
    store_external_ids = retail_faker.get_store_external_ids()
    fetchers = {eid: retail_faker.StoreFetcher(eid) for eid in store_external_ids}

    get_store_fetcher = unittest.mock.Mock(side_effect=lambda eid: fetchers[eid])

    monkeypatch.setattr(retail_faker, "StoreFetcher", get_store_fetcher)

    await fetch_and_save_stores_and_products(RetailChain.FAKER)

    stores_in_db = await db.select(db.stores)
    assert [Store(**row) for row in stores_in_db] == [
        fetcher.store for fetcher in fetchers.values()
    ]

    products_in_db = await db.select(db.products)
    assert [Product(**row) for row in products_in_db] == list(
        itertools.chain.from_iterable(fetcher.products for fetcher in fetchers.values())
    )
