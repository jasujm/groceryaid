import contextlib

import pytest

import groceryaid.db as db
from groceryaid.retail import Store, Price
import groceryaid.retail.sok
from groceryaid.retail.tasks import fetch_and_save_stores_and_prices
from groceryaid.settings import settings

from tests.factories import StoreFactory, PriceFactory


@pytest.mark.asyncio
async def test_fetch_store_and_prices(monkeypatch):
    store = StoreFactory()
    prices = PriceFactory.build_batch(6, store_id=store.id)

    class _FakeStoreFetcher(contextlib.AbstractAsyncContextManager):
        def __init__(self, store_external_id):
            assert store_external_id == store.external_id

        async def __aexit__(self, *args):
            return

        @staticmethod
        def get_store():
            return store

        @staticmethod
        async def get_prices_in_batches():
            yield prices[:3]
            yield prices[3:]

    def _create_fake_fetcher(store_external_id):
        assert store.external_id == store_external_id
        return fake_fetcher

    monkeypatch.setattr(settings, "sok_store_ids", [store.external_id])
    monkeypatch.setattr(groceryaid.retail.sok, "StoreFetcher", _FakeStoreFetcher)

    await fetch_and_save_stores_and_prices()

    stores_in_db = await db.read(db.stores)
    assert [Store(**row) for row in stores_in_db] == [store]

    prices_in_db = await db.read(db.prices)
    assert [Price(**row) for row in prices_in_db] == prices
