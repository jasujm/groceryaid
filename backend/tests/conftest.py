"""Common test configuration"""

import random

import hypothesis.strategies
import pytest
import pytest_asyncio
import sqlalchemy.ext.asyncio as sqlaio

from groceryaid import db
from groceryaid.retail import storevisits, Ean
from groceryaid.retail.faker import (
    StoreFactory,
    ProductFactory,
    CartProductFactory,
    StoreVisitFactory,
)


hypothesis.strategies.register_type_strategy(
    Ean, hypothesis.strategies.from_regex(Ean.prefix_pattern).map(Ean.from_prefix)
)


@pytest_asyncio.fixture(autouse=True)
async def database(monkeypatch):
    """Initializes in-memory database and returns the engine"""
    engine = sqlaio.create_async_engine("sqlite+aiosqlite://")
    monkeypatch.setattr("groceryaid.db._db.get_engine", lambda: engine)
    await db.init()
    return engine


@pytest_asyncio.fixture
async def store():
    """Return a store that will also be inserted into the database"""
    store = StoreFactory()
    await db.create(db.stores, store.dict())
    return store


@pytest_asyncio.fixture
async def products(store):
    """Return an array of products thta will also be inserted into the database"""
    products = ProductFactory.build_batch(10, store_id=store.id)
    await db.create(db.products, [product.dict() for product in products])
    return products


@pytest.fixture
def product(products):
    """Return a single product that will also be inserted into the database"""
    return random.choice(products)


@pytest_asyncio.fixture
async def variable_price_product(store):
    """Return a single product with variable price"""
    product = ProductFactory.build(ean="2000000000008", store_id=store.id)
    await db.create(db.products, product.dict())
    return product


@pytest_asyncio.fixture
async def storevisit(store, products):
    """Returns a store visit that will also be inserted into the database"""
    cartproducts = [
        CartProductFactory(
            product_id=product.id,
            ean=product.ean,
            name=product.name,
            price=product.price,
        )
        for product in products[:5]
    ]
    storevisit = StoreVisitFactory(
        store_id=store.id,
        cart=cartproducts,
    )
    await storevisits.create_store_visit(storevisit)
    return storevisit
