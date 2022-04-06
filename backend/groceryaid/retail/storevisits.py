"""Store visit services"""

import uuid
import typing

import sqlalchemy
import sqlalchemy.ext.asyncio as sqlaio

from .common import StoreVisit, _get_product_id

from .. import db


def _prepare_cart_for_db(storevisit: StoreVisit) -> list[dict]:
    return [
        {
            "storevisit_id": storevisit.id,
            "product_id": _get_product_id(storevisit.store_id, cartproduct.ean),
            **cartproduct.dict(include={"quantity"}),
        }
        for cartproduct in storevisit.cart
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
                    db.products.c.price,
                    db.cartproducts.c.quantity,
                ]
            )
            .select_from(db.cartproducts.join(db.products))
            .where(db.cartproducts.c.storevisit_id == id)
            .order_by(db.products.c.ean),
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
            & db.cartproducts.c.product_id.not_in(  # type: ignore
                _get_product_id(storevisit.store_id, cartproduct.ean)
                for cartproduct in storevisit.cart
            ),
            connection=conn,
        )
