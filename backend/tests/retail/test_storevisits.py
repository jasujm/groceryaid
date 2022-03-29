"""Test store visit services"""

import pytest

from groceryaid.retail import storevisits
from groceryaid.retail.faker import CartProductFactory


@pytest.mark.asyncio
async def test_read_store_visit(storevisit):
    assert await storevisits.read_store_visit(storevisit.id) == storevisit


@pytest.mark.asyncio
async def test_read_store_visit_nonexistent(faker):
    assert await storevisits.read_store_visit(faker.uuid4()) is None


@pytest.mark.asyncio
async def test_update_store_visit(storevisit, products):
    storevisit.cart[0].ean = products[-1].ean
    storevisit.cart[1].quantity += 1
    del storevisit.cart[-2:]
    storevisit.cart.append(CartProductFactory(ean=products[-2].ean))
    storevisit.cart.sort(key=lambda cp: cp.ean)
    await storevisits.update_store_visit(storevisit)
    assert await storevisits.read_store_visit(storevisit.id) == storevisit
