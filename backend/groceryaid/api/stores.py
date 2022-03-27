"""Stores API"""

import uuid

import fastapi

from .. import db

from .models import Store, Product

router = fastapi.APIRouter()


@router.get("/{id}", response_model=Store)
async def get_store(id: uuid.UUID):
    """
    Retrieve basic information about store identified by ``id``
    """
    if store := await db.read(
        db.stores, id, columns=[db.stores.c.chain, db.stores.c.name]
    ):
        return {"id": id, **store}
    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_404_NOT_FOUND,
        detail=f"Store {id=!r} not found",
    )


@router.get("/{store_id}/products/{ean}", response_model=Product)
async def get_product(store_id: uuid.UUID, ean: str):
    """
    Retrieve information about a product identified by store and EAN code
    """
    if product := await db.read(
        db.products,
        (db.products.c.store_id == store_id) & (db.products.c.ean == ean),
        columns=[db.products.c.name, db.products.c.price],
    ):
        return {
            "store": store_id,
            "ean": ean,
            **product,
        }
    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_404_NOT_FOUND,
        detail=f"Product {store_id=!r}, {ean=!r} not found",
    )
