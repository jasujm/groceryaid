"""Store visit services"""

import decimal
import uuid
import typing

import sqlalchemy
import sqlalchemy.ext.asyncio as sqlaio

from .common import StoreVisit, CartProduct, _get_product_id

from .. import db


def _prepare_cart_for_db(storevisit: StoreVisit) -> list[dict]:
    return [
        {
            "storevisit_id": storevisit.id,
            "product_id": _get_product_id(storevisit.store_id, cartproduct.ean),
            "rank": rank,
            "quantity": cartproduct.quantity,
            "price": cartproduct.price if cartproduct.is_variable_price() else None,
        }
        for (rank, cartproduct) in enumerate(storevisit.cart)
    ]


async def read_store_visit(
    id: uuid.UUID,
    *,
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
) -> typing.Optional[StoreVisit]:
    """Read store visit from database

    This retrieves the store visit, as well as the related cart.

    Parameters:
        id: The store visit id

    Keyword Arguments:
       connection: Database connection, or ``None`` to use a fresh connection
    """
    async with db.begin_connection(connection) as conn:
        storevisit = await db.read(
            db.storevisits,
            id,
            columns=[db.storevisits.c.store_id],
            connection=conn,
        )
        if storevisit is None:
            return None
        cartproducts = await db.execute(
            sqlalchemy.select(
                [
                    db.products.c.ean,
                    db.products.c.name,
                    sqlalchemy.func.coalesce(
                        db.cartproducts.c.price, db.products.c.price
                    ).label("price"),
                    db.cartproducts.c.quantity,
                ]
            )
            .select_from(db.cartproducts.join(db.products))
            .where(db.cartproducts.c.storevisit_id == id)
            .order_by(db.cartproducts.c.rank),
            connection=conn,
        )
    return StoreVisit(
        id=id,
        **storevisit,
        cart=cartproducts.fetchall(),
    )


async def create_store_visit(
    storevisit: StoreVisit,
    *,
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
):
    """Create store visit in database

    Parameters:
        storevisit: The store visit

    Keyword Arguments:
       connection: Database connection, or ``None`` to use a fresh connection
    """
    async with db.begin_connection(connection) as conn:
        await db.create(
            db.storevisits, storevisit.dict(exclude={"cart"}), connection=conn
        )
        if storevisit.cart:
            await db.create(
                db.cartproducts,
                _prepare_cart_for_db(storevisit),
                connection=conn,
            )


async def update_store_visit(
    storevisit: StoreVisit,
    *,
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
):
    """Update an existing store visit with dependencies

    Parameters:
        storevisit: The store visit

    Keyword Arguments:
       connection: Database connection, or ``None`` to use a fresh connection
    """
    async with db.begin_connection(connection) as conn:
        await db.update(
            db.storevisits,
            storevisit.dict(exclude={"store_id", "cart"}),
            connection=conn,
        )
        if storevisit.cart:
            await db.upsert(
                db.cartproducts,
                _prepare_cart_for_db(storevisit),
                connection=conn,
            )
        await db.delete(
            db.cartproducts,
            (db.cartproducts.c.storevisit_id == storevisit.id)
            & (db.cartproducts.c.rank >= len(storevisit.cart)),
            connection=conn,
        )


def _divide_cartproduct_to_bin_and_remaining(
    cartproduct: CartProduct, limit: decimal.Decimal
) -> tuple[typing.Optional[CartProduct], typing.Optional[CartProduct], decimal.Decimal]:
    assert cartproduct.price is not None
    if cartproduct.price > limit:
        return None, cartproduct, limit
    if cartproduct.quantity is None:
        return cartproduct, None, limit - cartproduct.price
    if cartproduct.price > 0:
        n_items_to_bin = min(int(limit / cartproduct.price), cartproduct.quantity)
    else:
        n_items_to_bin = cartproduct.quantity
    new_limit = limit - n_items_to_bin * cartproduct.price
    if n_items_to_bin == cartproduct.quantity:
        return cartproduct, None, new_limit
    n_items_remaining = cartproduct.quantity - n_items_to_bin
    return (
        cartproduct.copy(update={"quantity": n_items_to_bin}),
        cartproduct.copy(update={"quantity": n_items_remaining}),
        new_limit,
    )


def bin_pack_cart(
    cart: list[CartProduct], limit: decimal.Decimal
) -> list[list[CartProduct]]:
    """Apply bin packing to cart

    Groups the given ``cart`` into multiple bins in such a way that the total
    price of each cart remains below ``limit``.

    All the products whose price is higher than ``limit`` (and thus couldn't
    normally be placed in any bin) are returned as part of the last bin.

    Parameters:
        cart: A list of cart products
        limit: The target price limit per bin

    Returns:
        A list of lists of cart products, each containing one bin
    """
    cart_with_descending_prices = sorted(
        cart, key=lambda cartproduct: -cartproduct.price  # type: ignore
    )
    last_bin = []
    while (
        cart_with_descending_prices
        and (price := cart_with_descending_prices[0].price)
        and price > limit
    ):
        last_bin.append(cart_with_descending_prices.pop(0))
    bins = []
    next_bin = []
    limit_remaining = limit
    while cart_with_descending_prices:
        for i, cartproduct in enumerate(cart_with_descending_prices):
            (
                cartproduct_to_bin,
                cartproduct_remaining,
                limit_remaining,
            ) = _divide_cartproduct_to_bin_and_remaining(cartproduct, limit_remaining)
            if cartproduct_to_bin:
                next_bin.append(cartproduct_to_bin)
                if cartproduct_remaining:
                    cart_with_descending_prices[i] = cartproduct_remaining
                else:
                    cart_with_descending_prices.pop(i)
                break
        else:
            bins.append(next_bin)
            next_bin = []
            limit_remaining = limit
    if next_bin:
        bins.append(next_bin)
    if last_bin:
        bins.append(last_bin)
    return bins
