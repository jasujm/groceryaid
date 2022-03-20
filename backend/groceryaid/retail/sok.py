"""Retail definitions for S-Group (SOK)"""

import gql
import gql.transport.aiohttp as gql_aiohttp

from .common import RetailChain, Store, Price

from ..settings import settings

_store_and_products_query = gql.gql(
    """
    query {
      store(id:"726025995") {
        id,
        name,
        products(limit: 5) {
          from,
          total,
          limit,
          items {
            ean,
            name,
            price
          }
        }
      }
    }
    """
)


def _get_gql_client():
    return gql.Client(transport=gql_aiohttp.AIOHTTPTransport(url=settings.sok_api_url))


async def fetch_store_and_prices() -> tuple[Store, list[Price]]:
    """Fetch SOK stores and prices via external API"""
    async with _get_gql_client() as connection:
        result = await connection.execute(_store_and_products_query)
    store_dict = result["store"]
    store = Store(
        chain=RetailChain.SOK, external_id=store_dict["id"], name=store_dict["name"]
    )
    prices = [
        Price(store_id=store.id, **item) for item in store_dict["products"]["items"]
    ]
    return store, prices
