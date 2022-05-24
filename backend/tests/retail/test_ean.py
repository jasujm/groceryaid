"""
Test EAN utilities
"""

import decimal

from hypothesis import given, strategies as st

from groceryaid.retail import Ean

variable_price_ean_strategy = st.from_regex(Ean.variable_price_prefix_pattern).map(
    Ean.from_prefix
)

fixed_price_ean_strategy = (
    st.from_regex(Ean.prefix_pattern)
    .filter(lambda prefix: not Ean.variable_price_prefix_pattern.match(prefix))
    .map(Ean.from_prefix)
)


@given(variable_price_ean_strategy)
def test_variable_price_ean(ean):
    assert ean.is_variable_price()


@given(variable_price_ean_strategy)
def test_variable_price_ean_for_query(ean):
    ean_for_query = ean.get_ean_for_query()
    assert ean_for_query[:8] == ean[:8]
    assert ean_for_query[8:12] == "0000"


@given(variable_price_ean_strategy)
def test_variable_price_ean_get_price(ean):
    assert ean.get_price() == decimal.Decimal(ean[8:12]) / 100


@given(fixed_price_ean_strategy)
def test_fixed_price_ean(ean):
    assert not ean.is_variable_price()


@given(fixed_price_ean_strategy)
def test_fixed_price_ean_for_query(ean):
    assert ean.get_ean_for_query() == ean


@given(fixed_price_ean_strategy)
def test_fixed_price_ean_get_price(ean):
    assert ean.get_price() is None
