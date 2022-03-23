"""Utilities for generating fake store and price data for testing and development"""


import contextlib
import functools
import typing

from .common import Store, Price, RetailChain

try:
    import factory

except ImportError:

    if not typing.TYPE_CHECKING:

        # pylint: disable=all
        def StoreFactory():
            raise RuntimeError("StoreFactory and PriceFactory require factory module")

        PriceFactory = StoreFactory

else:

    class StoreFactory(factory.Factory):
        """Store factory"""

        class Meta:
            model = Store

        chain = RetailChain.FAKER
        external_id = factory.Sequence(str)
        name = factory.Faker("city")

    class PriceFactory(factory.Factory):
        """Price factory"""

        class Meta:
            model = Price

        store_id = factory.Faker("uuid4")
        ean = factory.Faker("ean")
        name = factory.Sequence(lambda n: f"Product {n}")
        price = factory.Faker("pydecimal", positive=True, max_value=10, right_digits=2)


class StoreFetcher(contextlib.AbstractAsyncContextManager):
    """Utility class for generating fake store and price data

    This class conforms to the general store fetcher protocol. Instead of
    accessing an external API, is simply generates some fake data for
    testing and development.

    Parameters:
        store_external_id: The external id of the store
    """

    def __init__(self, store_external_id: str):
        self.store = StoreFactory(external_id=store_external_id)
        self.prices = PriceFactory.build_batch(20, store_id=self.store.id)

    async def __aexit__(self, *args):
        pass

    def get_store(self) -> Store:
        """Get the fake store"""
        return self.store

    async def get_prices_in_batches(
        self,
    ) -> typing.AsyncIterable[list[Price]]:
        """Get the faked prices"""
        yield self.prices[:10]
        yield self.prices[10:]


@functools.cache
def get_store_external_ids() -> list[str]:
    """Return list of faked store ids"""
    return [store.external_id for store in StoreFactory.build_batch(2)]
