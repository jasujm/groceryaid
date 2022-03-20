import pytest

import groceryaid.db as db
from groceryaid.retail import Store, Price
import groceryaid.retail.sok
from groceryaid.retail.tasks import fetch_and_save_stores_and_prices

from tests.factories import StoreFactory, PriceFactory


@pytest.mark.asyncio
async def test_fetch_store_and_prices(monkeypatch):
    store = StoreFactory()
    prices = PriceFactory.build_batch(5, store_id=store.id)

    async def _fake_fetch_store_and_prices():
        return store, prices

    monkeypatch.setattr(
        groceryaid.retail.sok, "fetch_store_and_prices", _fake_fetch_store_and_prices
    )

    await fetch_and_save_stores_and_prices()

    stores_in_db = await db.read(db.stores)
    assert [Store(**row) for row in stores_in_db] == [store]

    prices_in_db = await db.read(db.prices)
    assert [Price(**row) for row in prices_in_db] == prices
