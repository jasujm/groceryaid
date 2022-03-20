"""Factories for generating test data"""

import factory

from groceryaid.retail import Store, Price, RetailChain


class StoreFactory(factory.Factory):
    """Store factory"""

    class Meta:
        model = Store

    chain = RetailChain.SOK
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
