"""Retail definitions for S-Group (SOK)"""

import gql
import gql.transport.aiohttp as gql_aiohttp

from .common import RetailChain, get_store_id

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
    # TODO: store URL in environment
    return gql.Client(
        transport=gql_aiohttp.AIOHTTPTransport(url="https://cfapi.voikukka.fi/graphql")
    )


async def fetch_store_and_prices():
    """Fetch SOK stores and prices via external API"""
    async with _get_gql_client() as connection:
        result = await connection.execute(_store_and_products_query)
    store = result["store"]
    store_id = get_store_id(RetailChain.SOK, store["id"])
    store_object = {
        "id": store_id,
        "chain": RetailChain.SOK.value,
        "external_id": store["id"],
        "name": store["name"],
    }
    price_objects = [
        {
            "store_id": store_id,
            **item,
        }
        for item in store["products"]["items"]
    ]
    return store_object, price_objects
