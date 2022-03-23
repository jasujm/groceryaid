import contextlib
import unittest.mock

import pytest

from groceryaid.retail import RetailChain
from groceryaid.retail.faker import StoreFactory, PriceFactory
from groceryaid.retail.sok import StoreFetcher


@pytest.mark.asyncio
async def test_fetch_and_store_prices(monkeypatch):

    store = StoreFactory(chain=RetailChain.SOK)
    prices = PriceFactory.build_batch(6, store_id=store.id)

    def _batch(from_: int):
        return {
            "store": {
                "id": store.external_id,
                "name": store.name,
                "products": {
                    "items": [
                        {"ean": price.ean, "name": price.name, "price": price.price}
                        for price in prices[from_ : from_ + 3]
                    ],
                },
            }
        }

    fake_connection = unittest.mock.Mock(
        execute=unittest.mock.AsyncMock(side_effect=[_batch(0), _batch(3), _batch(6)])
    )

    @contextlib.asynccontextmanager
    async def _fake_get_gql_client():
        yield fake_connection

    monkeypatch.setattr("groceryaid.retail.sok._get_gql_client", _fake_get_gql_client)

    async with StoreFetcher(store.external_id) as fetcher:
        assert fetcher.get_store() == store
        assert [price async for price in fetcher.get_prices_in_batches()] == [
            prices[:3],
            prices[3:],
        ]
