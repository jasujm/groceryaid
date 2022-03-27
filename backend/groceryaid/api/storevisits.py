"""Stores API"""

import uuid

import fastapi
import sqlalchemy

from .models import StoreVisit, StoreVisitCreate

from .. import db
from ..retail import storevisits

router = fastapi.APIRouter()


@router.get("/{id}", response_model=StoreVisit)
async def get_store_visit(id: uuid.UUID):
    """
    Retrieve information about store visit identified by ``id``
    """
    if storevisit := await storevisits.read_store_visit(id):
        store_id = storevisit.store_id
        return {
            "id": id,
            "store": store_id,
            "cart": [
                {
                    "product": (store_id, product.ean),
                    **product.dict(),
                }
                for product in storevisit.cart
            ],
        }
    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_404_NOT_FOUND,
        detail=f"Store visit {id=!r} not found",
    )


@router.post("", status_code=fastapi.status.HTTP_201_CREATED)
async def post_store_visit(
    storevisit: StoreVisitCreate, response: fastapi.Response, request: fastapi.Request
):
    """
    Create a new store visit
    """
    store_id = storevisit.store.key
    store = await db.read(db.stores, store_id, columns=[db.stores.c.id])
    if store is None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot create store visit with unknown store: {store_id!r}",
        )
    product_eans = set(cartproduct.product.key.ean for cartproduct in storevisit.cart)
    known_product_eans = set(
        row[0]
        for row in await db.execute(
            sqlalchemy.select([db.products.c.ean]).where(  # type: ignore
                db.products.c.store_id == store.id, db.products.c.ean.in_(product_eans)
            )
        )
    )
    if missing_eans := product_eans - known_product_eans:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot create store visit with unknown products: {missing_eans!r}",
        )
    new_storevisit = storevisits.StoreVisit(
        store_id=store.id,
        cart=[
            {
                "store_id": store.id,
                "ean": cartproduct.product.key.ean,
                **cartproduct.dict(),
            }
            for cartproduct in storevisit.cart
        ],
    )
    await storevisits.create_store_visit(new_storevisit)
    response.headers["Location"] = request.url_for(
        "get_store_visit", id=new_storevisit.id
    )
