import contextlib
import unittest.mock

import pytest

from groceryaid.retail import RetailChain
from groceryaid.retail.sok import fetch_store_and_prices

from tests.factories import StoreFactory, PriceFactory


@pytest.mark.asyncio
async def test_fetch_and_store_prices(monkeypatch):

    store = StoreFactory(chain=RetailChain.SOK)
    price = PriceFactory(store_id=store.id)

    fake_connection = unittest.mock.Mock(
        execute=unittest.mock.AsyncMock(
            return_value={
                "store": {
                    "id": store.external_id,
                    "name": store.name,
                    "products": {
                        "from": None,
                        "total": 100,
                        "limit": 100,
                        "items": [
                            {"ean": price.ean, "name": price.name, "price": price.price}
                        ],
                    },
                }
            }
        )
    )

    @contextlib.asynccontextmanager
    async def _fake_get_gql_client():
        yield fake_connection

    monkeypatch.setattr("groceryaid.retail.sok._get_gql_client", _fake_get_gql_client)
    assert await fetch_store_and_prices() == (store, [price])
