"""Test store visit services"""

import collections

from hypothesis import given, strategies as st
import pytest

from groceryaid.retail import storevisits, CartProduct
from groceryaid.retail.faker import CartProductFactory


@pytest.mark.asyncio
async def test_read_store_visit(storevisit):
    assert await storevisits.read_store_visit(storevisit.id) == storevisit


@pytest.mark.asyncio
async def test_read_store_visit_nonexistent(faker):
    assert await storevisits.read_store_visit(faker.uuid4()) is None


@pytest.mark.asyncio
async def test_update_store_visit(storevisit, products, variable_price_product):
    storevisit.cart[0].ean = products[-1].ean
    storevisit.cart[0].name = products[-1].name
    storevisit.cart[0].price = products[-1].price
    storevisit.cart[1].quantity += 1
    del storevisit.cart[-2:]
    storevisit.cart.append(
        CartProductFactory(
            ean=products[-2].ean, name=products[-2].name, price=products[-2].price
        )
    )
    storevisit.cart.append(
        CartProductFactory(
            ean=variable_price_product.ean,
            name=variable_price_product.name,
            quantity=None,
        )
    )
    storevisit.cart.sort(key=lambda cp: cp.ean)
    await storevisits.update_store_visit(storevisit)
    assert await storevisits.read_store_visit(storevisit.id) == storevisit


cartproducts_strategy = st.lists(
    st.builds(
        CartProduct,
        price=st.decimals(min_value=0, max_value=10, places=2),
        quantity=st.one_of(st.integers(min_value=1, max_value=10), st.none()),
    ),
    unique_by=lambda c: c.ean,
)

limit_strategy = st.decimals(min_value=0, max_value=20)


@given(cartproducts_strategy, limit_strategy)
def test_bin_pack_cart_replicates_original_quantities(cartproducts, limit):
    original_ean_counts = collections.Counter(
        {cp.ean: cp.quantity or 1 for cp in cartproducts}
    )
    binned_ean_counts = collections.Counter()
    for cart_bin in storevisits.bin_pack_cart(cartproducts, limit):
        for cartproduct in cart_bin:
            binned_ean_counts[cartproduct.ean] += cartproduct.quantity or 1
    assert original_ean_counts == binned_ean_counts


@given(cartproducts_strategy, limit_strategy)
def test_bin_pack_cart_keeps_bins_within_limit(cartproducts, limit):
    bins = storevisits.bin_pack_cart(cartproducts, limit)
    for cart_bin in bins[:-1]:
        assert sum(cartproduct.get_total_price() for cartproduct in cart_bin) <= limit
