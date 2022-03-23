"""Utilities for generating fake store and product data for testing and development"""


import contextlib
import functools
import typing

from .common import Store, Product, RetailChain

try:
    import factory

except ImportError:

    if not typing.TYPE_CHECKING:

        # pylint: disable=all
        def StoreFactory():
            raise RuntimeError("StoreFactory and ProductFactory require factory module")

        ProductFactory = StoreFactory

else:

    class StoreFactory(factory.Factory):
        """Store factory"""

        class Meta:
            model = Store

        chain = RetailChain.FAKER
        external_id = factory.Sequence(str)
        name = factory.Faker("city")

    class ProductFactory(factory.Factory):
        """Product factory"""

        class Meta:
            model = Product

        store_id = factory.Faker("uuid4")
        ean = factory.Faker("ean")
        name = factory.Sequence(lambda n: f"Product {n}")
        price = factory.Faker("pydecimal", positive=True, max_value=10, right_digits=2)


class StoreFetcher(contextlib.AbstractAsyncContextManager):
    """Utility class for generating fake store and product data

    This class conforms to the general store fetcher protocol. Instead of
    accessing an external API, is simply generates some fake data for
    testing and development.

    Parameters:
        store_external_id: The external id of the store
    """

    def __init__(self, store_external_id: str):
        self.store = StoreFactory(external_id=store_external_id)
        self.products = ProductFactory.build_batch(20, store_id=self.store.id)

    async def __aexit__(self, *args):
        pass

    def get_store(self) -> Store:
        """Get the fake store"""
        return self.store

    async def get_products_in_batches(
        self,
    ) -> typing.AsyncIterable[list[Product]]:
        """Get the faked products"""
        yield self.products[:10]
        yield self.products[10:]


@functools.cache
def get_store_external_ids() -> list[str]:
    """Return list of faked store ids"""
    return [store.external_id for store in StoreFactory.build_batch(2)]
