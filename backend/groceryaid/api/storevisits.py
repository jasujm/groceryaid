"""Stores API"""

import uuid

import fastapi

from .models import StoreVisit

from ..retail.storevisits import read_store_visit

router = fastapi.APIRouter()


@router.get("/{id}", response_model=StoreVisit)
async def get_store_visit(id: uuid.UUID):
    """
    Retrieve information about store visit identified by ``id``
    """
    if storevisit := await read_store_visit(id):
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
