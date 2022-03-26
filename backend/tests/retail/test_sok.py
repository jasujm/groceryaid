"""Test S-Group (SOK) services"""

import contextlib
import unittest.mock

import pytest

from groceryaid.retail import RetailChain
from groceryaid.retail.faker import StoreFactory, ProductFactory
from groceryaid.retail.sok import StoreFetcher


@pytest.mark.asyncio
async def test_fetch_and_store_products(monkeypatch):

    store = StoreFactory(chain=RetailChain.SOK)
    products = ProductFactory.build_batch(6, store_id=store.id)

    def _batch(from_: int):
        return {
            "store": {
                "id": store.external_id,
                "name": store.name,
                "products": {
                    "items": [
                        {
                            "ean": product.ean,
                            "name": product.name,
                            "price": product.price,
                        }
                        for product in products[from_ : from_ + 3]
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
        assert [product async for product in fetcher.get_products_in_batches()] == [
            products[:3],
            products[3:],
        ]
