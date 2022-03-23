"""Utilities for fetching S-Group store and product data"""

import contextlib
import typing

import gql
import gql.client
import gql.transport.aiohttp as gql_aiohttp

from .common import RetailChain, Store, Product

from ..settings import settings

_store_and_products_query = gql.gql(
    """
    query GetStoreAndProducts($store_id: ID!, $from: Int, $limit: Int) {
      store(id: $store_id) {
        id,
        name,
        products(from: $from, limit: $limit) {
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


def _get_gql_client() -> gql.Client:
    return gql.Client(transport=gql_aiohttp.AIOHTTPTransport(url=settings.sok_api_url))


class StoreFetcher(contextlib.AbstractAsyncContextManager):
    """Utility class for fetching store and product info via S-Group API

    Parameters:
        store_external_id: The external (S-Group API specific) id of the store
    """

    _cursor: int
    _gql_connection: gql.client.AsyncClientSession
    _gql_result: dict
    _store: Store

    def __init__(self, store_external_id: str):
        self._store_external_id = store_external_id
        self._gql_client = _get_gql_client()

    async def __aenter__(self) -> "StoreFetcher":
        self._cursor = 0
        self._gql_connection = await self._gql_client.__aenter__()
        store_dict = await self._fetch_next()
        self._store = Store(
            chain=RetailChain.SOK, external_id=store_dict["id"], name=store_dict["name"]
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        del self._gql_connection
        return await self._gql_client.__aexit__(exc_type, exc, tb)

    def get_store(self) -> Store:
        """Get the fetched store"""
        return self._store

    async def get_products_in_batches(self) -> typing.AsyncIterable[list[Product]]:
        """Get products in batches

        The fetcher makes calls to external API and fetches in batches whose
        size is determined in the settings. It ends when either products in
        external API are exhausted or the setting specific limit is reached.
        """
        products = self._parse_products()
        yield products
        while products and (
            not settings.sok_products_fetch_limit
            or self._cursor < settings.sok_products_fetch_limit
        ):
            await self._fetch_next()
            products = self._parse_products()
            if products:
                yield products

    async def _fetch_next(self):
        self._gql_result = await self._gql_connection.execute(
            _store_and_products_query,
            {
                "store_id": self._store_external_id,
                "from": self._cursor,
                "limit": settings.sok_products_batch_size,
            },
        )
        store = self._gql_result["store"]
        self._cursor += len(store["products"]["items"])
        return store

    def _parse_products(self):
        items = self._gql_result["store"]["products"]["items"]
        return [Product(store_id=self._store.id, **item) for item in items]


def get_store_external_ids() -> list[str]:
    """Return list of known S-Group stores"""
    return settings.sok_store_ids
