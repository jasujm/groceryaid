"""Test store visit services"""

import pytest

from groceryaid.retail import storevisits


@pytest.mark.asyncio
async def test_read_store_visit(storevisit):
    assert await storevisits.read_store_visit(storevisit.id) == storevisit


@pytest.mark.asyncio
async def test_read_store_visit_nonexistent(faker):
    assert await storevisits.read_store_visit(faker.uuid4()) is None
