import asyncio
import uuid
import enum

import gql
import gql.transport.aiohttp as gql_aiohttp

from . import db

# Select your transport with a defined url endpoint
transport = gql_aiohttp.AIOHTTPTransport(url="https://cfapi.voikukka.fi/graphql")

gql_client = gql.Client(transport=transport)

# TODO: use variables and fancy stuff like that
sok_store_and_products_query = gql.gql(
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

# TODO: store in environment
store_root_namespace = uuid.uuid4()


class RetailChain(enum.Enum):
    """Identifies grocery store chain

    Each chain is assumed to have distinct API to fetch products/prices.
    """
    SOK = "sok"


store_namespaces = {
    chain: uuid.uuid5(store_root_namespace, str(chain)) for chain in RetailChain
}


def get_store_id(chain: RetailChain, store_id):
    return uuid.uuid5(store_namespaces[chain], str(store_id))


async def download_prices_sok():
    async with gql_client as gql_conn, db.engine.begin() as db_conn:
        chain = RetailChain.SOK
        result = await gql_conn.execute(sok_store_and_products_query)
        store = result["store"]
        store_id = get_store_id(chain, store["id"])
        await db_conn.execute(
            db.stores.insert(),
            {
                "id": store_id,
                "chain": chain.value,
                "external_id": store["id"],
                "name": store["name"],
            },
        )
        await db_conn.execute(
            db.prices.insert(),
            [
                {
                    "store_id": store_id,
                    **item,
                }
                for item in store["products"]["items"]
            ],
        )


if __name__ == "__main__":
    asyncio.run(download_prices_sok())
