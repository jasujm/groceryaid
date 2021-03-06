"""Utilities for generating fake store and product data for testing and development"""


import contextlib
import functools
import typing

from .common import RetailChain, Store, Product, StoreVisit, CartProduct

try:
    import factory

except ImportError:

    if not typing.TYPE_CHECKING:

        # pylint: disable=all
        class Factory:
            def __init__(self, *args, **kwargs):
                raise RuntimeError(
                    f"Using {self.__class__.__name__} requires factory module"
                )

        class StoreFactory(Factory):
            pass

        class ProductFactory(Factory):
            pass

        class CartProductFactory(Factory):
            pass

        class StoreVisitFactory(Factory):
            pass

else:

    from faker import Faker

    _faker = Faker()

    def _fixed_price_ean():
        while True:
            ean = _faker.ean()
            if not ean.startswith("2"):
                return ean

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
        ean = factory.LazyFunction(_fixed_price_ean)
        name = factory.Sequence(lambda n: f"Product {n}")
        price = factory.Faker("pydecimal", positive=True, max_value=10, right_digits=2)

    class CartProductFactory(factory.Factory):
        """Cart product factory"""

        class Meta:
            model = CartProduct

        ean = factory.LazyFunction(_fixed_price_ean)
        name = factory.Sequence(lambda n: f"Cart product {n}")
        price = factory.Faker("pydecimal", positive=True, max_value=10, right_digits=2)
        quantity = factory.Faker("pyint", min_value=1, max_value=5)

    class StoreVisitFactory(factory.Factory):
        """Store visit factory"""

        class Meta:
            model = StoreVisit

        store_id = factory.Faker("uuid4")
        cart = factory.LazyFunction(lambda: CartProductFactory.build_batch(5))

        @factory.post_generation
        def _sort_cart(self, *args, **kwargs):
            self.cart.sort(key=lambda cp: cp.ean)


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
