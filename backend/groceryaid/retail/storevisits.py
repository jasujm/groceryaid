"""Store visit services"""

import uuid
import typing

import sqlalchemy

from .common import StoreVisit

from .. import db


async def read_store_visit(id: uuid.UUID) -> typing.Optional[StoreVisit]:
    """Read store visit from database

    This retrieves the store visit, as well as the related cart.

    Parameters:
        id: The store visit id
    """
    async with db.get_connection() as connection:
        storevisit = await db.read(
            db.storevisits,
            id,
            columns=[db.storevisits.c.store_id],
            connection=connection,
        )
        if storevisit is None:
            return None
        cartproducts = await db.execute(
            sqlalchemy.select([db.cartproducts.c.ean, db.cartproducts.c.quantity])
            .where(db.cartproducts.c.storevisit_id == id)
            .order_by(db.cartproducts.c.ean),
            connection=connection,
        )
    return StoreVisit(id=id, **storevisit, cart=cartproducts.fetchall())


async def create_store_visit(storevisit: StoreVisit):
    """Create store visit in database

    Parameters:
        storevisit: The store visit
    """
    async with db.get_connection() as connection:
        await db.create(
            db.storevisits, storevisit.dict(exclude={"cart"}), connection=connection
        )
        await db.create(
            db.cartproducts,
            [
                {"storevisit_id": storevisit.id, **cartproduct.dict()}
                for cartproduct in storevisit.cart
            ],
            connection=connection,
        )